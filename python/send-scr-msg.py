import asyncio
import time
import re
from indy import crypto, did, wallet

# Step 5 code goes here, replacing the prep() stub.
async def prep(wallet_handle, my_vk, their_vk, msg):
    encrypted = await crypto.auth_crypt(wallet_handle, my_vk, their_vk, str.encode(msg))
    print('encrypted = %s' % repr(encrypted))
    with open('encrypted.dat', 'wb') as f:
        f.write(bytes(encrypted))


# Step 3 code goes here, replacing the init() stub.
async def init():
    me = input('Who are you? ').strip()
    wallet_name = '%s-wallet' % me

    # 1. Create Wallet and Get Wallet Handle
    try:
        await wallet.create_wallet('pool1', wallet_name, None, None, None)
    except:
        pass
    wallet_handle = await wallet.open_wallet(wallet_name, None, None)
    print('wallet = %s' % wallet_handle)

    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")
    print('my_did and verkey = %s %s' % (my_did, my_vk))

    their = input("Other party's DID and verkey? ").strip().split(' ')
    return wallet_handle, my_did, my_vk, their[0], their[1]

# Step 6 code goes here, replacing the read() stub.
async def read(wallet_handle, my_vk):
    with open('encrypted.dat', 'rb') as f:
        encrypted = f.read()
    decrypted = await crypto.auth_decrypt(wallet_handle, my_vk, encrypted)
    msg = decrypted.__getitem__(1).decode()
    print(msg)

async def demo():
    wallet_handle, my_did, my_vk, their_did, their_vk = await init()

    while True:
        argv = input('> ').strip().split(' ')
        cmd = argv[0].lower()
        rest = ' '.join(argv[1:])
        if re.match(cmd, 'prep'):
            await prep(wallet_handle, my_vk, their_vk, rest)
        elif re.match(cmd, 'read'):
            await read(wallet_handle, my_vk)
        elif re.match(cmd, 'quit'):
            break
        else:
            print('Huh?')

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(demo())
        time.sleep(1)  # waiting for libindy thread complete
    except KeyboardInterrupt:
        print('')

