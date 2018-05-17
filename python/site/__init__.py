import aiohttp
from aiohttp import web

async def init(request):
    agent = request.app
    data = json.loads(await request.read())
    agent['me'] = data['me']

    wallet_name = '%s-wallet' % agent['me']
    try:
        await wallet.create_wallet('pool1', wallet_name, None, None, None)
    except:
        pass

    agent['wallet_handle'] = await wallet.open_wallet(wallet_name, None, None)
    agent['initialized'] = True

def agent_ready(agent):
    return agent['initialized']

def redirect_to_init():
    raise web.HTTPFound('/init')

def require_init(agent):
    if not agent_ready(agent):
        redirect_to_init()
