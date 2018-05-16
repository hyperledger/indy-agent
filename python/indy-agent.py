import asyncio
import os
from indy import did, wallet, pool

from receiver.aiohttp_receiver import AioHttpReceiver as Receiver
from router.simple_router import SimpleRouter as Router
import modules.connection as connection
import serializer.json_serializer as Serializer

q = asyncio.Queue()
loop = asyncio.get_event_loop()

port = os.environ('INDY_AGENT_PORT')
if not port:
    port = 8080

receiver = Receiver(q, port)
router = Router()

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

    return wallet_handle

async def main():
    wallet_handle = await init()
    await router.register("CONN_REQ", connection.handle_request)
    while True:
        msg_bytes = await receiver.recv()
        print("Message received:\n\tbytes: {}".format(msg_bytes))
        msg = Serializer.unpack(msg_bytes)
        print("\tType: {}, Data: {}".format(msg.type, msg.data))
        await router.route(msg, wallet_handle)

try:
    loop.create_task(receiver.start(loop))
    loop.create_task(main())
    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
