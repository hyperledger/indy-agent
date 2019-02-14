""" Module to handle the connection process.
"""

# pylint: disable=import-error

import json
import base64
import uuid
import re

import aiohttp
from indy import crypto, did, pairwise, non_secrets

import indy_sdk_utils as utils
import serializer.json_serializer as Serializer
from router.simple_router import SimpleRouter
from . import Module
from message import Message
from helpers import serialize_bytes_json, bytes_to_str, str_to_bytes

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

        record = uuid.uuid4().hex

        await self.agent.send_admin_message(Message({
            '@type': AdminConnection.INVITE_RECEIVED,
            'label': invite_msg['label'],
            'key': invite_msg['recipientKeys'][0],
            'endpoint': invite_msg['serviceEndpoint']
        }))

        await non_secrets.add_wallet_record(
            self.agent.wallet_handle,
            'invitation',
            invite_msg['recipientKeys'][0],
            Serializer.pack(invite_msg),
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
                  "DID": "B.did@B:A",
                  "DIDDoc": {
                      // did Doc here.
                  }
                }
        """
        invite = Serializer.unpack(
            json.loads(
                await non_secrets.get_wallet_record(
                    self.agent.wallet_handle,
                    'invitation',
                    msg['key'],
                    '{}'
                )
            )['value']
        )

        my_label = self.agent.owner
        label = invite['label']
        their_connection_key = invite['recipientKeys'][0]
        their_endpoint = invite['serviceEndpoint']

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
                'DID': my_did,
                'DIDDoc': {
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

        await self.agent.send_admin_message(
            Message({
                '@type': AdminConnection.REQUEST_SENT,
                'label': label
            })
        )

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
                  "DID":"A.did@A:B",
                  "DIDDoc": {
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
            'connection': {
                'DID': my_did,
                'DIDDoc': {
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

        await self.agent.send_message_to_agent(their_did, response_msg)

        await self.agent.send_admin_message(
            Message({
                '@type': AdminConnection.RESPONSE_SENT,
                'label': label,
                'did': their_did
            })
        )

class Connection(Module):

    FAMILY_NAME = "connections"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    INVITE = FAMILY + "invitation"
    REQUEST = FAMILY + "request"
    RESPONSE = FAMILY + "response"


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
                      "DID": "B.did@B:A",
                      "DIDDoc": {
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
        connection_key = msg.context['to_key']

        label = msg['label']
        their_did = msg['connection']['DID']
        # NOTE: these values are pulled based on the minimal connectathon format. Full processing
        #  will require full DIDDoc storage and evaluation.
        their_vk = msg['connection']['DIDDoc']['publicKey'][0]['publicKeyBase58']
        their_endpoint = msg['connection']['DIDDoc']['service'][0]['serviceEndpoint']

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
                'their_endpoint': their_endpoint,
                'their_vk': their_vk,
                'my_vk': my_vk,
                'connection_key': connection_key  # used to sign the response
            })
        )

        await self.agent.send_admin_message(
            Message({
                '@type': AdminConnection.REQUEST_RECEIVED,
                'label': label,
                'did': their_did,
                'endpoint': their_endpoint,
                'history': msg
            })
        )


    async def response_received(self, msg: Message) -> Message:
        """ Process response

            Response format:
                {
                  "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/response",
                  "DID":"A.did@A:B",
                  "DIDDoc": {
                      //did doc
                  }
                }
        """
        my_did = msg.context['to_did']
        my_vk = await did.key_for_local_did(self.agent.wallet_handle, my_did)

        #process signed field
        msg['connection'], sig_verified = await self.agent.unpack_and_verify_signed_agent_message_field(msg['connection~sig'])
        # connection~sig remains for metadata


        their_did = msg['connection']['DID']
        their_vk = msg['connection']['DIDDoc']['publicKey'][0]['publicKeyBase58']
        their_endpoint = msg['connection']['DIDDoc']['service'][0]['serviceEndpoint']

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
                'my_vk': my_vk
            })
        )

        # Pairwise connection between agents is established at this point
        await self.agent.send_admin_message(
            Message({
                '@type': AdminConnection.RESPONSE_RECEIVED,
                'label': label,
                'their_did': their_did,
                'history': msg
            })
        )
