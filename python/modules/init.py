""" Handle agent initialization.
"""

# pylint: disable=import-error

from aiohttp import web
from indy import wallet

async def initialize_agent(request):
    """ Initialize agent.
    """
    agent = request.app['agent']
    data = await request.post()
    agent.owner = data['agent_name']
    agent.endpoint = data['endpoint']

    wallet_name = '%s-wallet' % agent.owner

    # pylint: disable=bare-except
    # TODO: better handle potential exceptions.
    try:
        await wallet.create_wallet('pool1', wallet_name, None, None, None)
    except:
        pass

    try:
        agent.wallet_handle = await wallet.open_wallet(wallet_name, None, None)
    except:
        print("Could not open wallet!")
        raise web.HTTPBadRequest()

    agent.initialized = True

    raise web.HTTPFound('/')
