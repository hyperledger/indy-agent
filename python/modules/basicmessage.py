import aiohttp
import aiohttp_jinja2
import jinja2
import base64
import json
from indy import did, wallet, pairwise, crypto

from helpers import str_to_bytes, serialize_bytes_json, bytes_to_str
from router.simple_router import SimpleRouter
import serializer.json_serializer as Serializer
from agent import Agent, WalletConnectionException
from message import Message
from message_types import BASICMESSAGE, ADMIN_BASICMESSAGE, CONN, FORWARD
from . import Module

class BasicMessage(Module):

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(BASICMESSAGE.MESSAGE, self.receive_message)
        self.router.register(ADMIN_BASICMESSAGE.SEND_MESSAGE, self.send_message)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def send_message(self, msg: Message) -> Message:
        """ UI activated method.
        """

        their_did_str = msg['content']['their_did']
        message_to_send = msg['content']['message']

        pairwise_conn_info_str = await pairwise.get_pairwise(self.agent.wallet_handle, their_did_str)
        pairwise_conn_info_json = json.loads(pairwise_conn_info_str)

        my_did_str = pairwise_conn_info_json['my_did']

        data_to_send = json.dumps(
            {
                "message": message_to_send
            }
        )

        data_to_send_bytes = str_to_bytes(data_to_send)

        metadata_json = json.loads(pairwise_conn_info_json['metadata'])
        conn_name = metadata_json['conn_name']
        their_endpoint = metadata_json['their_endpoint']
        their_verkey_str = metadata_json['their_verkey']

        my_did_info_str = await did.get_my_did_with_meta(self.agent.wallet_handle,
                                                         my_did_str)
        my_did_info_json = json.loads(my_did_info_str)
        my_verkey_str = my_did_info_json['verkey']

        inner_msg = Message({
            '@type': BASICMESSAGE.MESSAGE,
            'to': "did:sov:ABC",
            'content': serialize_bytes_json(
                await crypto.auth_crypt(self.agent.wallet_handle, my_verkey_str,
                                        their_verkey_str, data_to_send_bytes))
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
            '@type': ADMIN_BASICMESSAGE.MESSAGE_SENT,
            'id': self.agent.ui_token,
            'content': {'name': conn_name}
        })


    async def receive_message(self, msg: Message) -> Message:
        my_did_str = msg['did']
        their_did_str = ""
        conn_name = ""
        my_verkey = ""

        self.agent_pairwises_list_str = await pairwise.list_pairwise(self.agent.wallet_handle)
        self.agent_pairwises_list = json.loads(self.agent_pairwises_list_str)

        for self.agent_pairwise_str in self.agent_pairwises_list:
            self.agent_pairwise_json = json.loads(self.agent_pairwise_str)
            if not self.agent_pairwise_json['my_did'] == my_did_str:
                continue
            their_did_str = self.agent_pairwise_json['their_did']

            metadata_str = self.agent_pairwise_json['metadata']
            metadata_json = json.loads(metadata_str)
            conn_name = metadata_json['conn_name']
            my_verkey = metadata_json['my_verkey']

        message_bytes = str_to_bytes(msg['content'])
        message_bytes = base64.b64decode(message_bytes)

        their_key_str, their_data_bytes = await crypto.auth_decrypt(
            self.agent.wallet_handle, my_verkey, message_bytes)

        their_data_json = json.loads(bytes_to_str(their_data_bytes))

        return Message({
            '@type': ADMIN_BASICMESSAGE.MESSAGE_RECEIVED,
            'id': self.agent.ui_token,
            'content': {'name': conn_name,
                     'their_did': their_did_str,
                     'history': their_data_json}
        })
