import asyncio
import os
import sys
from indy import did, wallet, pool

from receiver.aiohttp_receiver import AioHttpReceiver as Receiver
from router.simple_router import SimpleRouter as Router
import modules.connection as connection
import serializer.json_serializer as Serializer

q = asyncio.Queue()
in_q = asyncio.Queue()

loop = asyncio.get_event_loop()

if 'INDY_AGENT_PORT' in os.environ.keys():
    port = int(os.environ['INDY_AGENT_PORT'])
else:
    port = 8080

receiver = Receiver(q, port)
router = Router()

wallet_handle = None
me = None

async def init():
    me = input('Who are you? ').strip()
    wallet_name = '%s-wallet' % me

    #Create Wallet and Get Wallet Handle
    #Node pool must be running
    try:
        await wallet.create_wallet('pool1', wallet_name, None, None, None)
    except:
        pass

    wallet_handle = await wallet.open_wallet(wallet_name, None, None)
    print('wallet = %s' % wallet_handle)

async def main():
    await init()

    await router.register("CONN_REQ", connection.handle_request)
    await router.register("CONN_RES", connection.handle_response)

    while True:
        print('would you like to send a connection request? [Y/n]')
        msg_bytes = await receiver.recv()
        print("Message received:\n\tbytes: {}".format(msg_bytes))
        msg = Serializer.unpack(msg_bytes)
        print("\tType: {}, Data: {}".format(msg.type, msg.data))
        await router.route(msg, wallet_handle)

def cli():
    ans = sys.stdin.readline().strip()
    if ans == '' or ans[0].lower() == 'y':
        loop.create_task(connection.send_request(1, 'bob'))

try:
    loop.add_reader(sys.stdin, cli)
    loop.create_task(receiver.start(loop))
    loop.create_task(main())
    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
