import json
from indy import wallet

async def initialize_agent(request):
    agent = request.app['agent']
    # data = json.loads(await request.read())
    data = await request.post()
    agent.me = data['agent_name']

    wallet_name = '%s-wallet' % agent.me
    try:
       await wallet.create_wallet('pool1', wallet_name, None, None, None)
    except:
        pass
    finally:
        agent.wallet_handle = await wallet.open_wallet(wallet_name, None, None)
        agent.initialized = True
