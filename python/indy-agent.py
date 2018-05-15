import asyncio
from indy import crypto, did, wallet

from receiver.aiohttp_receiver import AioHttpReceiver

q = asyncio.Queue()
loop = asyncio.get_event_loop()

receiver = AioHttpReceiver(q, 8080)

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
    while True:
        msg = await receiver.recv()
        print(msg)

try:
    loop.create_task(receiver.start(loop))
    loop.create_task(main())
    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
