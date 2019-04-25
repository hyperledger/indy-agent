""" Module to handle the connection process.
"""

# pylint: disable=import-error

import json
import base64
import uuid
import re
import datetime

import aiohttp
from indy import crypto, did, pairwise, non_secrets, error

import indy_sdk_utils as utils
import serializer.json_serializer as Serializer
from router.simple_router import SimpleRouter
from . import Module
from message import Message
from helpers import serialize_bytes_json, bytes_to_str, str_to_bytes
from test_suite.tests.connection import Connection as ConnectionValidator


class BadInviteException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class AdminConnection(Module):
    FAMILY_NAME = "admin_connections"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    # Message Types in this family
    CONNECTION_LIST = FAMILY + "connection_list"
    CONNECTION_LIST_REQUEST = FAMILY + "connection_list_request"

    GENERATE_INVITE = FAMILY + "generate_invite"
    INVITE_GENERATED = FAMILY + "invite_generated"
    INVITE_RECEIVED = FAMILY + "invite_received"
    RECEIVE_INVITE = FAMILY + "receive_invite"

    SEND_REQUEST = FAMILY + "send_request"
    REQUEST_SENT = FAMILY + "request_sent"
    REQUEST_RECEIVED = FAMILY + "request_received"

    SEND_RESPONSE = FAMILY + "send_response"
    RESPONSE_SENT = FAMILY + "response_sent"
    RESPONSE_RECEIVED = FAMILY + "response_received"

    def __init__(self, agent):
        self.agent = agent

        self.router = SimpleRouter()
        self.router.register(AdminConnection.GENERATE_INVITE, self.generate_invite)
        self.router.register(AdminConnection.RECEIVE_INVITE, self.receive_invite)
        self.router.register(AdminConnection.SEND_REQUEST, self.send_request)
        self.router.register(AdminConnection.SEND_RESPONSE, self.send_response)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def generate_invite(self, msg: Message) -> Message:
        """ Generate new connection invitation.

            This interaction represents an out-of-band communication channel. In the future and in
            practice, these sort of invitations will be received over any number of channels such as
            SMS, Email, QR Code, NFC, etc.

            Structure of an invite message:

                {
                    "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/invitation",
                    "label": "Alice",
                    "did": "did:sov:QmWbsNYhMrjHiqZDTUTEJs"
                }

            Or, in the case of a peer DID:

                {
                    "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/invitation",
                    "label": "Alice",
                    "did": "did:peer:oiSqsNYhMrjHiqZDTUthsw",
                    "key": "8HH5gYEeNc3z7PYXmd54d4x6qAfCNrqQqEB3nS7Zfu7K",
                    "endpoint": "https://example.com/endpoint"
                }

            Currently, only peer DID is supported.
        """
        connection_key = await did.create_key(self.agent.wallet_handle, "{}")

        # Store connection key
        await non_secrets.add_wallet_record(
            self.agent.wallet_handle,
            'connection_key',
            connection_key,
            connection_key,
            '{}'
        )

        invite_msg = Message({
            '@type': Connection.INVITE,
            'label': self.agent.owner,
            'recipientKeys': [connection_key],
            'serviceEndpoint': self.agent.endpoint,
            # routingKeys not specified, but here is where they would be put in the invite.
        })

        b64_invite = \
            base64.urlsafe_b64encode(bytes(Serializer.pack(invite_msg), 'utf-8')).decode('ascii')

        await self.agent.send_admin_message(
            Message({
                '@type': AdminConnection.INVITE_GENERATED,
                'invite': '{}?c_i={}'.format(self.agent.endpoint, b64_invite)
            })
        )

    async def receive_invite(self, msg: Message) -> Message:
        """ Receive and save invite.

            This interaction represents an out-of-band communication channel. In the future and in
            practice, these sort of invitations will be received over any number of channels such as
            SMS, Email, QR Code, NFC, etc.

            In this iteration, invite messages are received from the admin interface as a URL
            after being copied and pasted from another agent instance.

            The URL is formatted as follows:

                https://<domain>/<path>?c_i=<invitationstring>

            The invitation string is a base64 url encoded json string.

            Structure of an invite message:

                {
                    "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/invitation",
                    "label": "Alice",
                    "did": "did:sov:QmWbsNYhMrjHiqZDTUTEJs"
                }

            Or, in the case of a peer DID:

                {
                    "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/invitation",
                    "label": "Alice",
                    "key": "8HH5gYEeNc3z7PYXmd54d4x6qAfCNrqQqEB3nS7Zfu7K",
                    "endpoint": "https://example.com/endpoint"
                }

            Currently, only peer DID format is supported.
        """

        # Parse invite string
        matches = re.match("(.+)?c_i=(.+)", msg['invite'])
        if not matches:
            raise BadInviteException("Invite string is improperly formatted")

        invite_msg = Serializer.unpack(
            base64.urlsafe_b64decode(matches.group(2)).decode('utf-8')
        )

        pending_connection = Message({
            '@type': AdminConnection.INVITE_RECEIVED,
            'label': invite_msg['label'],
            'connection_key': invite_msg['recipientKeys'][0],
            'endpoint': invite_msg['serviceEndpoint'],
            'history': [{
                'date': str(datetime.datetime.now()),
                'msg': invite_msg.to_dict()
            }],
            'status': "Invite Received"
        })
        await self.agent.send_admin_message(pending_connection)

        await non_secrets.add_wallet_record(
            self.agent.wallet_handle,
            'invitations',
            invite_msg['recipientKeys'][0],
            Serializer.pack(pending_connection),
            '{}'
        )

    async def send_request(self, msg: Message):
        """ Recall invite message from wallet and prepare and send request to the inviter.

            send_request message format:

                {
                  "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/admin_connections/1.0/send_request",
                  "key": <key sent in invite>
                }

            Request format:

                {
                  "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",
                  "label": "Bob",
                  "did": "B.did@B:A",
                  "did_doc": {
                      // did Doc here.
                  }
                }
        """
        pending_connection = Serializer.unpack(
            json.loads(
                await non_secrets.get_wallet_record(
                    self.agent.wallet_handle,
                    'invitations',
                    msg['connection_key'],
                    '{}'
                )
            )['value']
        )

        my_label = self.agent.owner
        label = pending_connection['label']
        their_connection_key = pending_connection['connection_key']
        their_endpoint = pending_connection['endpoint']

        # Create my information for connection
        (my_did, my_vk) = await utils.create_and_store_my_did(self.agent.wallet_handle)

        await did.set_did_metadata(
            self.agent.wallet_handle,
            my_did,
            json.dumps({
                'label': label,
                'their_endpoint': their_endpoint
            })
        )

        # Send Connection Request to inviter
        request = Message({
            '@type': Connection.REQUEST,
            'label': my_label,
            'connection': {
                'did': my_did,
                'did_doc': {
                    "@context": "https://w3id.org/did/v1",
                    "id": my_did,
                    "publicKey": [{
                        "id": my_did + "#keys-1",
                        "type": "Ed25519VerificationKey2018",
                        "controller": my_did,
                        "publicKeyBase58": my_vk
                    }],
                    "service": [{
                        "id": my_did + ";indy",
                        "type": "IndyAgent",
                        "recipientKeys": [my_vk],
                        #"routingKeys": ["<example-agency-verkey>"],
                        "serviceEndpoint": self.agent.endpoint,
                    }],
                }
            }
        })

        await self.agent.send_message_to_endpoint_and_key(
            my_vk,
            their_connection_key,
            their_endpoint,
            request
        )

        pending_connection['@type'] = AdminConnection.REQUEST_SENT
        pending_connection['status'] = "Request Sent"
        pending_connection['history'].append({
            'date': str(datetime.datetime.now()),
            'msg': msg.to_dict()})
        await non_secrets.update_wallet_record_value(self.agent.wallet_handle,
                                                     'invitations',
                                                     pending_connection['connection_key'],
                                                     Serializer.pack(pending_connection))

        await self.agent.send_admin_message(pending_connection)

    async def send_response(self, msg: Message) -> Message:
        """ Send response to request.

            send_response message format:

                {
                  "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/admin_connections/1.0/send_response",
                  "did": <did of request sender>
                }

            Response format:
                {
                  "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/response",
                  "did":"A.did@A:B",
                  "did_doc": {
                      //did doc
                  }
                }
        """
        their_did = msg['did']

        pairwise_info = json.loads(await pairwise.get_pairwise(self.agent.wallet_handle, their_did))
        pairwise_meta = json.loads(pairwise_info['metadata'])

        my_did = pairwise_info['my_did']
        label = pairwise_meta['label']
        my_vk = await did.key_for_local_did(self.agent.wallet_handle, my_did)

        response_msg = Message({
            '@type': Connection.RESPONSE,
            '~thread': { 'thid': pairwise_meta['req_id'] },
            'connection': {
                'did': my_did,
                'did_doc': {
                    "@context": "https://w3id.org/did/v1",
                    "id": my_did,
                    "publicKey": [{
                        "id": my_did + "#keys-1",
                        "type": "Ed25519VerificationKey2018",
                        "controller": my_did,
                        "publicKeyBase58": my_vk
                    }],
                    "service": [{
                        "id": my_did + ";indy",
                        "type": "IndyAgent",
                        "recipientKeys": [my_vk],
                        #"routingKeys": ["<example-agency-verkey>"],
                        "serviceEndpoint": self.agent.endpoint,
                    }],
                }
            }
        })

        # Apply signature to connection field, sign it with the key used in the invitation and request
        response_msg['connection~sig'] = await self.agent.sign_agent_message_field(response_msg['connection'], pairwise_meta["connection_key"])
        del response_msg['connection']

        pending_connection = Serializer.unpack(
            json.loads(
                await non_secrets.get_wallet_record(self.agent.wallet_handle,
                                                    'invitations',
                                                    pairwise_meta['connection_key'],
                                                    '{}')
            )['value']
        )
        pending_connection['status'] = "Response Sent"
        pending_connection['@type'] = AdminConnection.RESPONSE_SENT
        pending_connection['history'].append({
            'date': str(datetime.datetime.now()),
            'msg': msg.to_dict()})

        await self.agent.send_message_to_agent(their_did, response_msg)

        await self.agent.send_admin_message(pending_connection)

        await non_secrets.delete_wallet_record(self.agent.wallet_handle,
                                               'invitations',
                                               pairwise_meta['connection_key'])

class Connection(Module):

    FAMILY_NAME = "connections"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    INVITE = FAMILY + "invitation"
    REQUEST = FAMILY + "request"
    RESPONSE = FAMILY + "response"
    REQUEST_NOT_ACCEPTED = "request_not_accepted"

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(Connection.REQUEST, self.request_received)
        self.router.register(Connection.RESPONSE, self.response_received)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def request_received(self, msg: Message) -> Message:
        """ Received connection request.

            Request format:

                {
                  "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",
                  "label": "Bob",
                  "connection":{
                      "did": "B.did@B:A",
                      "did_doc": {
                          "@context": "https://w3id.org/did/v1",
                          "publicKey": [{
                            "id": "did:example:123456789abcdefghi#keys-1",
                            "type": "Ed25519VerificationKey2018",
                            "controller": "did:example:123456789abcdefghi",
                            "publicKeyBase58": "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
                          }],
                          "service": [{
                            "type": "IndyAgent",
                            "recipientKeys" : [ "<verkey>" ], //pick one
                            "routingKeys": ["<example-agency-verkey>"],
                            "serviceEndpoint": "https://example.agency.com",
                          }]
                      }
                  }
                }
        """
        try:
            ConnectionValidator.Request.validate(msg)
        except Exception as e:
            vk, endpoint = ConnectionValidator.Request.extract_verkey_endpoint(msg)
            if None in (vk, endpoint):
                # Cannot extract verkey and endpoint hence won't send any message back.
                print('Encountered error parsing connection request ', e)
            else:
                # Sending an error message back to the sender
                err_msg = self.build_problem_report_for_connections(Connection.FAMILY, Connection.REQUEST_NOT_ACCEPTED,
                                                                    str(e))
                await self.agent.send_message_to_endpoint_and_key(vk, endpoint, err_msg)
            return

        connection_key = msg.context['to_key']

        label = msg['label']
        their_did = msg['connection']['did']
        # NOTE: these values are pulled based on the minimal connectathon format. Full processing
        #  will require full DIDDoc storage and evaluation.
        their_vk = msg['connection']['did_doc']['publicKey'][0]['publicKeyBase58']
        their_endpoint = msg['connection']['did_doc']['service'][0]['serviceEndpoint']

        # Store their information from request
        await utils.store_their_did(self.agent.wallet_handle, their_did, their_vk)

        await did.set_did_metadata(
            self.agent.wallet_handle,
            their_did,
            json.dumps({
                'label': label,
                'endpoint': their_endpoint,

            })
        )

        # Create my information for connection
        (my_did, my_vk) = await utils.create_and_store_my_did(self.agent.wallet_handle)

        # Create pairwise relationship between my did and their did
        await pairwise.create_pairwise(
            self.agent.wallet_handle,
            their_did,
            my_did,
            json.dumps({
                'label': label,
                'req_id': msg['@id'],
                'their_endpoint': their_endpoint,
                'their_vk': their_vk,
                'my_vk': my_vk,
                'connection_key': connection_key  # used to sign the response
            })
        )

        pending_connection = Message({
            '@type': AdminConnection.REQUEST_RECEIVED,
            'label': label,
            'did': their_did,
            'connection_key': connection_key,
            'endpoint': their_endpoint,
            'history': [{
                'date': str(datetime.datetime.now()),
                'msg': msg.to_dict()}],
            'status': "Request Received"
            # routingKeys not specified, but here is where they would be put in the invite.
        })
        try:
            await non_secrets.add_wallet_record(
                self.agent.wallet_handle,
                'invitations',
                connection_key,
                Serializer.pack(pending_connection),
                '{}'
            )
        except error.IndyError as indy_error:
            if indy_error.error_code == error.ErrorCode.WalletItemAlreadyExists:
                pass
            raise indy_error
        await self.agent.send_admin_message(pending_connection)




    async def response_received(self, msg: Message) -> Message:
        """ Process response

            Response format:
                {
                  "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/response",
                  "did":"A.did@A:B",
                  "did_doc": {
                      //did doc
                  }
                }
        """
        my_did = msg.context['to_did']
        my_vk = await did.key_for_local_did(self.agent.wallet_handle, my_did)

        #process signed field
        msg['connection'], sig_verified = await self.agent.unpack_and_verify_signed_agent_message_field(msg['connection~sig'])
        # connection~sig remains for metadata


        their_did = msg['connection']['did']
        their_vk = msg['connection']['did_doc']['publicKey'][0]['publicKeyBase58']
        their_endpoint = msg['connection']['did_doc']['service'][0]['serviceEndpoint']

        msg_vk = msg.context['from_key']
        # TODO: verify their_vk (from did doc) matches msg_vk

        # Retrieve connection information from DID metadata
        my_did_meta = json.loads(
            await did.get_did_metadata(self.agent.wallet_handle, my_did)
        )
        label = my_did_meta['label']

        # Clear DID metadata. This info will be stored in pairwise meta.
        await did.set_did_metadata(self.agent.wallet_handle, my_did, '')

        # In the final implementation, a signature will be provided to verify changes to
        # the keys and DIDs to be used long term in the relationship.
        # Both the signature and signature check are omitted for now until specifics of the
        # signature are decided.

        # Store their information from response
        await utils.store_their_did(self.agent.wallet_handle, their_did, their_vk)

        await did.set_did_metadata(
            self.agent.wallet_handle,
            their_did,
            json.dumps({
                'label': label,
                'endpoint': their_endpoint
            })
        )

        # Create pairwise relationship between my did and their did
        await pairwise.create_pairwise(
            self.agent.wallet_handle,
            their_did,
            my_did,
            json.dumps({
                'label': label,
                'their_endpoint': their_endpoint,
                'their_vk': their_vk,
                'my_vk': my_vk,
                'connection_key': msg.data['connection~sig']['signer']
            })
        )

        pending_connection = Serializer.unpack(
            json.loads(
                await non_secrets.get_wallet_record(self.agent.wallet_handle,
                                                    'invitations',
                                                    msg.data['connection~sig']['signer'],
                                                    '{}')
            )['value']
        )
        pending_connection['status'] = "Response Received"
        pending_connection['@type'] = AdminConnection.RESPONSE_RECEIVED
        pending_connection['history'].append({
            'date': str(datetime.datetime.now()),
            'msg': msg.to_dict()})

        # Pairwise connection between agents is established at this point
        await self.agent.send_admin_message(pending_connection)

        # Delete invitation
        await non_secrets.delete_wallet_record(self.agent.wallet_handle,
                                               'invitations',
                                               msg.data['connection~sig']['signer'])
