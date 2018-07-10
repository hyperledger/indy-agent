import json
from aiohttp import web
from model import Message, Agent
from message_types import UI

async def ui_connect(_, agent: Agent) -> Message:
    return Message(
        UI.STATE,
        None, # No ID needed
        {
            'initialized': agent.initialized,
            'agent_name': agent.owner,
            'connections': [conn for _, conn in agent.connections.items()]
        }
    )

async def root(request):
    agent = request.app['agent']
    agent.endpoint = request.url.scheme + '://' + request.url.host
    if request.url.port is not None:
        agent.endpoint += ':' + str(request.url.port) + '/indy'
    else:
        agent.endpoint += '/indy'
    return web.FileResponse('view/index.html')
