""" Module to handle the connection process.
"""

# pylint: disable=import-error

import json
import base64
import uuid

import aiohttp
from indy import crypto, did, pairwise, non_secrets

import serializer.json_serializer as Serializer
from router.simple_router import SimpleRouter
from . import Module
from message import Message
from message_types import ADMIN_CONNECTIONS, CONN, FORWARD
from helpers import serialize_bytes_json, bytes_to_str, str_to_bytes

class Connection(Module):

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(CONN.INVITE, self.invite_received)
        self.router.register(CONN.REQUEST, self.request_received)
        self.router.register(CONN.RESPONSE, self.response_received)

        self.router.register(ADMIN_CONNECTIONS.SEND_INVITE, self.send_invite)
        self.router.register(ADMIN_CONNECTIONS.SEND_REQUEST, self.send_request)
        self.router.register(ADMIN_CONNECTIONS.SEND_RESPONSE, self.send_response)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)


    async def send_invite(self, msg: Message) -> Message:
        """ UI activated method.
        """

        their_endpoint = msg['endpoint']
        conn_name = msg['name']

        (endpoint_did_str, connection_key) = await did.create_and_store_my_did(self.agent.wallet_handle, "{}")

        meta_json = json.dumps(
            {
                "conn_name": conn_name
            }
        )

        await did.set_did_metadata(self.agent.wallet_handle, endpoint_did_str, meta_json)

        msg = Message({
            '@type':CONN.INVITE,
            'content':{
                'name': conn_name,
                'endpoint': {
                    'url': self.agent.endpoint,
                },
                'connection_key': connection_key
            }
        })
        serialized_msg = Serializer.pack(msg)
        async with aiohttp.ClientSession() as session:
            async with session.post(their_endpoint, data=serialized_msg) as resp:
                print(resp.status)
                print(await resp.text())

        return Message({
            '@type': ADMIN_CONNECTIONS.INVITE_SENT,
            'id': self.agent.ui_token,
            'content': {'name': conn_name}
        })


    async def invite_received(self, msg: Message) -> Message:
        conn_name = msg['content']['name']
        their_endpoint = msg['content']['endpoint']
        their_connection_key = msg['content']['connection_key']

        # store invite in the wallet
        await non_secrets.add_wallet_record(self.agent.wallet_handle,
            "invitation", uuid.uuid4().hex,
            json.dumps({
            'name': conn_name,
            'endpoint': their_endpoint,
            'connection_key': their_connection_key
        }), json.dumps({}))

        return Message({
            '@type': ADMIN_CONNECTIONS.INVITE_RECEIVED,
            'content': {'name': conn_name,
                     'endpoint': their_endpoint,
                     'connection_key': their_connection_key,
                     'history': msg}
        })


    async def send_request(self, msg: Message) -> Message:
        """ UI activated method.
        """

        # read invitation from wallet if id present. otherwise, use values from args

        their_endpoint = msg['content']['endpoint']
        conn_name = msg['content']['name']
        their_connection_key = msg['content']['key']

        my_endpoint_uri = self.agent.endpoint

        (my_endpoint_did_str, my_connection_key) = await did.create_and_store_my_did(self.agent.wallet_handle, "{}")

        data_to_send = json.dumps(
            {
                "did": my_endpoint_did_str,
                "key": my_connection_key
            }
        )

        data_to_send_bytes = str_to_bytes(data_to_send)

        meta_json = json.dumps(
            {
                "conn_name": conn_name,
                "their_endpoint": their_endpoint
            }
        )

        await did.set_did_metadata(self.agent.wallet_handle, my_endpoint_did_str, meta_json)

        inner_msg = Message({
            '@type': CONN.REQUEST,
            'to': "did:sov:ABC",
            'endpoint': my_endpoint_uri,
            'content': serialize_bytes_json(await crypto.auth_crypt(self.agent.wallet_handle, my_connection_key, their_connection_key, data_to_send_bytes))
        })

        outer_msg = Message({
            '@type': FORWARD.FORWARD_TO_KEY,
            'to': "ABC",
            'content': inner_msg
        })

        serialized_outer_msg = Serializer.pack(outer_msg)

        serialized_outer_msg_bytes = str_to_bytes(serialized_outer_msg)

        all_message = Message({
            '@type': CONN.REQUEST,
            'content': serialize_bytes_json(
                await crypto.anon_crypt(their_connection_key,
                                        serialized_outer_msg_bytes))
        })

        serialized_msg = Serializer.pack(all_message)

        async with aiohttp.ClientSession() as session:
            async with session.post(their_endpoint, data=serialized_msg) as resp:
                print(resp.status)
                print(await resp.text())

        return Message({
            '@type': ADMIN_CONNECTIONS.REQUEST_SENT,
            'id': self.agent.ui_token,
            'content': {'name': conn_name}
        })


    async def request_received(self, msg: Message) -> Message:
        their_endpoint_uri = msg['endpoint']

        my_did_str = msg['did']
        my_did_info_str = await did.get_my_did_with_meta(self.agent.wallet_handle, my_did_str)
        my_did_info_json = json.loads(my_did_info_str)

        my_verkey = my_did_info_json['verkey']
        metadata_str = my_did_info_json['metadata']
        metadata_dict = json.loads(metadata_str)

        conn_name = metadata_dict['conn_name']

        message_bytes = str_to_bytes(msg['content'])
        message_bytes = base64.b64decode(message_bytes)

        their_key_str, their_data_bytes = await crypto.auth_decrypt(
            self.agent.wallet_handle, my_verkey, message_bytes)

        # change verkey passed via send_invite to the agent without encryption
        my_new_verkey = await did.replace_keys_start(self.agent.wallet_handle, my_did_str, '{}')
        await did.replace_keys_apply(self.agent.wallet_handle, my_did_str)

        their_data_json = json.loads(bytes_to_str(their_data_bytes))

        their_did_str = their_data_json['did']

        identity_json = json.dumps(
            {
                "did": their_did_str,
                "verkey": their_key_str
            }
        )

        meta_json = json.dumps(
            {
                "conn_name": conn_name,
                "their_endpoint": their_endpoint_uri,
                "their_verkey": their_key_str,
                "my_verkey": my_new_verkey
            }
        )

        await did.store_their_did(self.agent.wallet_handle, identity_json)
        await pairwise.create_pairwise(self.agent.wallet_handle, their_did_str, my_did_str, meta_json)

        return Message({
            '@type': ADMIN_CONNECTIONS.REQUEST_RECEIVED,
            'content': {
                'name': conn_name,
                'endpoint_did': their_did_str,
                'history': msg
            }
        })


    async def send_response(self, msg: Message) -> Message:
        """ UI activated method.
        """

        their_did_str = msg['content']['endpoint_did']

        pairwise_conn_info_str = await pairwise.get_pairwise(self.agent.wallet_handle, their_did_str)
        pairwise_conn_info_json = json.loads(pairwise_conn_info_str)

        my_did_str = pairwise_conn_info_json['my_did']

        data_to_send = json.dumps(
            {
                "did": my_did_str
            }
        )

        data_to_send_bytes = str_to_bytes(data_to_send)

        metadata_json = json.loads(pairwise_conn_info_json['metadata'])
        conn_name = metadata_json['conn_name']
        their_endpoint = metadata_json['their_endpoint']
        their_verkey_str = metadata_json['their_verkey']

        my_did_info_str = await did.get_my_did_with_meta(self.agent.wallet_handle, my_did_str)
        my_did_info_json = json.loads(my_did_info_str)
        my_verkey_str = my_did_info_json['verkey']

        inner_msg = Message({
            '@type': CONN.RESPONSE,
            'to': "did:sov:ABC",
            'content': serialize_bytes_json(await crypto.auth_crypt(
                self.agent.wallet_handle, my_verkey_str, their_verkey_str, data_to_send_bytes))
        })

        outer_msg = Message({
            '@type': FORWARD.FORWARD,
            'to': "ABC",
            'content': inner_msg
        })

        serialized_outer_msg = Serializer.pack(outer_msg)

        serialized_outer_msg_bytes = str_to_bytes(serialized_outer_msg)

        all_message = Message({
            'content': serialize_bytes_json(await crypto.anon_crypt(their_verkey_str,
                                                                 serialized_outer_msg_bytes))
        })

        serialized_msg = Serializer.pack(all_message)

        async with aiohttp.ClientSession() as session:
            async with session.post(their_endpoint, data=serialized_msg) as resp:
                print(resp.status)
                print(await resp.text())

        return Message({
            '@type': ADMIN_CONNECTIONS.RESPONSE_SENT,
            'id': self.agent.ui_token,
            'content': {'name': conn_name}
        })


    async def response_received(self, msg: Message) -> Message:
        my_did_str = msg['did']

        my_did_info_str = await did.get_my_did_with_meta(self.agent.wallet_handle, my_did_str)
        my_did_info_json = json.loads(my_did_info_str)

        my_verkey = my_did_info_json['verkey']
        metadata_str = my_did_info_json['metadata']
        metadata_dict = json.loads(metadata_str)

        conn_name = metadata_dict['conn_name']
        their_endpoint = metadata_dict['their_endpoint']

        message_bytes = str_to_bytes(msg['content'])
        message_bytes = base64.b64decode(message_bytes)

        their_key_str, their_data_bytes = await crypto.auth_decrypt(
            self.agent.wallet_handle, my_verkey, message_bytes)

        their_data_json = json.loads(bytes_to_str(their_data_bytes))

        their_did_str = their_data_json['did']

        identity_json = json.dumps(
            {
                "did": their_did_str,
                "verkey": their_key_str
            }
        )

        meta_json = json.dumps(
            {
                "conn_name": conn_name,
                "their_endpoint": their_endpoint,
                "their_verkey": their_key_str,
                "my_verkey": my_verkey
            }
        )

        await did.store_their_did(self.agent.wallet_handle, identity_json)
        await pairwise.create_pairwise(self.agent.wallet_handle, their_did_str, my_did_str, meta_json)

        #  pairwise connection between agents is established to this point
        return Message({
            '@type': ADMIN_CONNECTIONS.RESPONSE_RECEIVED,
            'id': self.agent.ui_token,
            'content': {'name': conn_name,
                     'their_did': their_did_str,
                     'history': msg}
        })
