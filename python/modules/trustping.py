import aiohttp
import aiohttp_jinja2
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

class AdminTrustPing(Module):
    FAMILY_NAME = "admin_trustping"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    TRUSTPING_RECEIVED = FAMILY + "trustping_received"
    SEND_TRUSTPING = FAMILY + "send_trustping"
    TRUSTPING_SENT = FAMILY + "trustping_sent"
    TRUSTPING_RESPONSE = FAMILY + "trustping_reponse"
    GET_TRUSTPINGS = FAMILY + "get_trustpings"
    MESSAGES = FAMILY + "trustping"

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(AdminTrustPing.SEND_TRUSTPING, self.send_trustping)
        self.router.register(AdminTrustPing.GET_TRUSTPINGS, self.get_trustpings)
        self.router.register(AdminTrustPing.TRUSTPING_RESPONSE, self.trustping_response)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def trustping_response(self, msg: Message) -> Message:
        print("trustping_response")
        print(msg)


    async def send_trustping(self, msg: Message) -> Message:
        """ UI activated method.
        """
        print("send_trustping")
        # This lookup block finds the from address from the to address. This should be fixed, so that the from address
        #  comes in the admin message.
        their_did_str = msg['to']
        pairwise_conn_info_str = await pairwise.get_pairwise(self.agent.wallet_handle, their_did_str)
        pairwise_conn_info_json = json.loads(pairwise_conn_info_str)
        my_did_str = pairwise_conn_info_json['my_did']

        message_to_send = msg['message']
        time_sent = time.time()

        # store message in the wallet
        # await non_secrets.add_wallet_record(
        #     self.agent.wallet_handle,
        #     "trustping",
        #     uuid.uuid4().hex,
        #     json.dumps({
        #         'from': my_did_str,
        #         'timestamp': time_sent,
        #         'content': message_to_send
        #     }),
        #     json.dumps({
        #         "their_did": their_did_str
        #     })
        # )

        message = Message({
            '@type': TrustPing.MESSAGE,
            '@timestamp': time_sent,
            'content': message_to_send
        })

        await self.agent.send_message_to_agent(their_did_str, message)

        await self.agent.send_admin_message(
            Message({
                '@type': AdminTrustPing.TRUSTPING_SENT,
                'id': self.agent.ui_token,
                'with': their_did_str,
                'message': {
                    'from': my_did_str,
                    'timestamp': time_sent,
                    'content': message_to_send
                }
            })
        )

    async def get_trustpings(self, msg: Message) -> Message:
        their_did = msg['with']
        print("get_trustpings")
        # search_handle = await non_secrets.open_wallet_search(
        #     self.agent.wallet_handle, "trustping",
        #     json.dumps({"their_did": their_did}),
        #     json.dumps({})
        # )
        # results = await non_secrets.fetch_wallet_search_next_records(self.agent.wallet_handle, search_handle, 100)

        # messages = []
        # for r in json.loads(results)["records"] or []: # records is None if empty
        #     d = json.loads(r['value'])
        #     d["_id"] = r["id"] # include record id for further reference.
        #     messages.append(d)
        # #TODO: fetch in loop till all records are processed
        # await non_secrets.close_wallet_search(search_handle)
        # messages = sorted(messages, key=lambda n: n['timestamp'], reverse=True)
        #Trustping stored on pingee
        #Wire for trustping received

        await self.agent.send_admin_message(
            Message({
                '@type': AdminTrustPing.MESSAGES,
                'with': their_did,
            })
        )
        # Pause for a second before sending back response

        await self.agent.send_message_to_agent(their_did, "Sending trust ping back")


class TrustPing(Module):
    FAMILY_NAME = "trustping"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    MESSAGE = FAMILY + "trustping"

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(TrustPing.MESSAGE, self.receive_message)
        # self.router.register(TrustPing.SENDBACKTRUSTPING, self)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def receive_message(self, msg: Message) -> Message:

        await self.agent.send_admin_message(
            Message({
                '@type': AdminTrustPing.TRUSTPING_RECEIVED,
                '@id': self.agent.ui_token,
                'with': msg.context['from_did'],
                'message': {
                    'from': msg.context['from_did'],
                    # 'timestamp': msg['timestamp'],
                    'content': msg['content']
                }
            })
        )
        time.sleep(15)
        await self.agent.send_message_to_agent(
            msg.context['from_did'],
            Message({
                '@type': AdminTrustPing.TRUSTPING_RESPONSE,
                '@id': self.agent.ui_token,
                'with': msg.context['from_did']
            })
        )

        # Respond back with a timestamp when it received it
        # Daniel Hardman's intitial draft of TrustPing
        # {
        #     "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/trust_ping/1.0/ping",
        #     "@id": "518be002-de8e-456e-b3d5-8fe472477a86",
        #     "@timing": {
        #         "out_time": "2018-12-15 04:29:23Z",
        #         "expires_time": "2018-12-15 05:29:23Z",
        #         "delay_milli": 0
        #     },
        #     "comment_ltxt": "Hi. Are you listening?",
        #     "response_requested": true
        # }

        # Send this back
        # {
        #     "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/trust_ping/1.0/ping_response",
        #     "@thread": {"thid": "518be002-de8e-456e-b3d5-8fe472477a86", "seqnum": 0},
        #    dont need "@timing": {"@in_time": "2018-12-15 04:29:28Z", "@out_time": "2018-12-15 04:31:00Z"},
        #     "comment_ltxt": "Hi yourself. I'm here."
        #  }