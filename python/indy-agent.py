import asyncio
from indy import crypto, did, wallet

from receiver.aiohttp_receiver import AioHttpReceiver as Receiver
from router.simple_router import SimpleRouter as Router
import modules.connection as connection
from packager.message import Message

q = asyncio.Queue()
loop = asyncio.get_event_loop()

receiver = Receiver(q, 8080)
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

    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")
    print('my_did and verkey = %s %s' % (my_did, my_vk))

    return wallet_handle, my_did, my_vk

async def main():
    wallet_handle, my_did, my_vk = await init()
    await router.register("CONN_REQ", connection.handle_request)
    while True:
        msg_bytes = await receiver.recv()
        print(msg_bytes)
        msg = Message.from_json(msg_bytes)
        print(msg)
        await router.route(msg, wallet_handle)

try:
    loop.create_task(receiver.start(loop))
    loop.create_task(main())
    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
