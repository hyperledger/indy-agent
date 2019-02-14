import aiohttp
import aiohttp_jinja2
import datetime
import jinja2
import base64
import json
import time
import uuid
from indy import did, wallet, pairwise, crypto, non_secrets

from helpers import str_to_bytes, serialize_bytes_json, bytes_to_str
from router.simple_router import SimpleRouter
import serializer.json_serializer as Serializer
from agent import Agent, WalletConnectionException
from message import Message
from . import Module

class AdminBasicMessage(Module):
    FAMILY_NAME = "admin_basicmessage"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    MESSAGE_RECEIVED = FAMILY + "message_received"
    SEND_MESSAGE = FAMILY + "send_message"
    MESSAGE_SENT = FAMILY + "message_sent"
    GET_MESSAGES = FAMILY + "get_messages"
    MESSAGES = FAMILY + "messages"

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(AdminBasicMessage.SEND_MESSAGE, self.send_message)
        self.router.register(AdminBasicMessage.GET_MESSAGES, self.get_messages)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def send_message(self, msg: Message) -> Message:
        """ UI activated method.
        """

        # This lookup block finds the from address from the to address. This should be fixed, so that the from address
        #  comes in the admin message.
        their_did_str = msg['to']
        pairwise_conn_info_str = await pairwise.get_pairwise(self.agent.wallet_handle, their_did_str)
        pairwise_conn_info_json = json.loads(pairwise_conn_info_str)
        my_did_str = pairwise_conn_info_json['my_did']

        message_to_send = msg['message']
        sent_time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(' ')

        # store message in the wallet
        await non_secrets.add_wallet_record(
            self.agent.wallet_handle,
            "basicmessage",
            uuid.uuid4().hex,
            json.dumps({
                'from': my_did_str,
                'sent_time': sent_time,
                'content': message_to_send
            }),
            json.dumps({
                "their_did": their_did_str
            })
        )

        message = Message({
            '@type': BasicMessage.MESSAGE,
            '~l10n': {'locale': 'en'},
            'sent_time': sent_time,
            'content': message_to_send
        })

        await self.agent.send_message_to_agent(their_did_str, message)

        await self.agent.send_admin_message(
            Message({
                '@type': AdminBasicMessage.MESSAGE_SENT,
                'id': self.agent.ui_token,
                'with': their_did_str,
                'message': {
                    'from': my_did_str,
                    'sent_time': sent_time,
                    'content': message_to_send
                }
            })
        )

    async def get_messages(self, msg: Message) -> Message:
        their_did = msg['with']
        search_handle = await non_secrets.open_wallet_search(
            self.agent.wallet_handle, "basicmessage",
            json.dumps({"their_did": their_did}),
            json.dumps({})
        )
        results = await non_secrets.fetch_wallet_search_next_records(self.agent.wallet_handle, search_handle, 100)

        messages = []
        for r in json.loads(results)["records"] or []: # records is None if empty
            d = json.loads(r['value'])
            d["_id"] = r["id"] # include record id for further reference.
            messages.append(d)
        #TODO: fetch in loop till all records are processed
        await non_secrets.close_wallet_search(search_handle)
        messages = sorted(messages, key=lambda n: n['sent_time'], reverse=True)

        await self.agent.send_admin_message(
            Message({
                '@type': AdminBasicMessage.MESSAGES,
                'with': their_did,
                'messages': messages
            })
        )


class BasicMessage(Module):
    FAMILY_NAME = "basicmessage"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    MESSAGE = FAMILY + "message"

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(BasicMessage.MESSAGE, self.receive_message)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def receive_message(self, msg: Message) -> Message:

        # store message in the wallet
        await non_secrets.add_wallet_record(
            self.agent.wallet_handle,
            "basicmessage",
            uuid.uuid4().hex,
            json.dumps({
                'from': msg.context['from_did'],
                'sent_time': msg['sent_time'],
                'content': msg['content']
            }),
            json.dumps({
                "their_did": msg.context['from_did']
            })
        )

        await self.agent.send_admin_message(
            Message({
                '@type': AdminBasicMessage.MESSAGE_RECEIVED,
                'id': self.agent.ui_token,
                'with': msg.context['from_did'],
                'message': {
                    'from': msg.context['from_did'],
                    'sent_time': msg['sent_time'],
                    'content': msg['content']
                }
            })
        )
