import aiohttp_jinja2
import jinja2
import json
from indy import did, wallet, non_secrets

from router.simple_router import SimpleRouter
from agent import Agent
from message import Message
from message_types import ADMIN
from . import Module

class Admin(Module):

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(ADMIN.STATE_REQUEST, self.state_request)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def state_request(self, _) -> Message:

        invitations = []
        if self.agent.initialized:
            search_handle = await non_secrets.open_wallet_search(self.agent.wallet_handle, "invitations",
                                                                 json.dumps({}),
                                                                 json.dumps({'retrieveTotalCount': True}))
            results = await non_secrets.fetch_wallet_search_next_records(self.agent.wallet_handle, search_handle, 100)

            for r in json.loads(results)["records"] or []: # records is None if empty
                d = json.loads(r['value'])
                d["_id"] = r["id"] # include record id for further reference.
                invitations.append(d)
            #TODO: fetch in loop till all records are processed
            await non_secrets.close_wallet_search(search_handle)

        return Message({
            '@type': ADMIN.STATE,
            'content': {
                'initialized': self.agent.initialized,
                'agent_name': self.agent.owner,
                'invitations': invitations
            }
        })


@aiohttp_jinja2.template('index.html')
async def root(request):
    print(request)
    agent = request.app['agent']
    agent.offer_endpoint = request.url.scheme + '://' + request.url.host
    print(agent.offer_endpoint)
    agent.endpoint = request.url.scheme + '://' + request.url.host
    if request.url.port is not None:
        agent.endpoint += ':' + str(request.url.port) + '/indy'
        agent.offer_endpoint += ':' + str(request.url.port) + '/offer'
    else:
        agent.endpoint += '/indy'
        agent.offer_endpoint += '/offer'
    return {'ui_token': agent.ui_token}
