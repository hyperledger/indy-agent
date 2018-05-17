import asyncio
import os
import sys
from aiohttp import web
from indy import did, wallet, pool

from receiver.aiohttp_receiver import AioHttpReceiver as Receiver
from router.simple_router import SimpleRouter as Router
import modules.connection as connection
import serializer.json_serializer as Serializer


if 'INDY_AGENT_PORT' in os.environ.keys():
    port = int(os.environ['INDY_AGENT_PORT'])
else:
    port = 8080

loop = asyncio.get_event_loop()
agent = web.Application()
agent['msg_router'] = Router()
agent['msg_receiver'] =  Receiver(asyncio.Queue())

agent.add_routes([web.post('/indy', agent['msg_receiver'].handle_message)])


agent.add_routes([web.static('/', os.path.realpath('site/'))])


runner = web.AppRunner(agent)
loop.run_until_complete(runner.setup())

site = web.TCPSite(runner, 'localhost', port)

async def init(agent):
    agent['me'] = input('Who are you? ').strip()
    wallet_name = '%s-wallet' % agent['me']

    #Create Wallet and Get Wallet Handle
    try:
        await wallet.create_wallet('pool1', wallet_name, None, None, None)
    except:
        pass

    agent['wallet_handle'] = await wallet.open_wallet(wallet_name, None, None)


async def main(agent):
    msg_router = agent['msg_router']
    msg_receiver = agent['msg_receiver']

    await msg_router.register("CONN_REQ", connection.handle_request)
    await msg_router.register("CONN_RES", connection.handle_response)

    while True:
        msg_bytes = await msg_receiver.recv()
        msg = Serializer.unpack(msg_bytes)
        await msg_router.route(msg, agent['wallet_handle'])

def cli():
    ans = sys.stdin.readline().strip()
    if ans == '' or ans[0].lower() == 'y':
        loop.create_task(connection.send_request(1, 'bob'))

try:
    loop.run_until_complete(init(agent))
    print('wallet = {}, me = {}'.format(agent['wallet_handle'], agent['me']))

    loop.create_task(site.start())
    loop.create_task(main(agent))

    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
