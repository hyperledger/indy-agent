import asyncio
import time
import re
import json
import aiohttp
from indy import crypto, did, wallet, pairwise

'''
    decrypts anoncrypted connection response
'''
#async def handle_response(self, data, wallet_handle):
#    decrypted = await crypto.auth_decrypt(wallet_handle, my_vk, data)
#    msg = decrypted.__getitem__(1).decode()
#    print(msg)

'''
    Handles connection requests from other peers.
'''
async def handle_request(msg, wallet_handle):
    #TODO: validate correct format for incoming data
    data = msg.data
    did_str = msg.did
    endpoint = data['endpoint']
    verkey = data['verkey']
    owner = data['owner']

    #accept = input('{} would like to connect with you. Accept? [Y/n]'.format(owner)).strip()
    #if accept != '' and accept[0].lower() != 'y':
    #    return

    ident_json = json.dumps({
                             "did": did_str,
                             "verkey": verkey
                             })

    meta_json = json.dumps({
                            "owner": owner,
                            "endpoint": endpoint
                            })

    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")
    print('my_did and verkey = %s %s' % (my_did, my_vk))

    await did.store_their_did(wallet_handle, ident_json)
    print("did and verkey stored")

    await did.set_endpoint_for_did(wallet_handle, did_str, endpoint, verkey)
    #print("endpoint stored")

    #print(meta_json)
    await did.set_did_metadata(wallet_handle, did_str, meta_json)
    print("meta_data stored")

    await pairwise.create_pairwise(wallet_handle, did_str, my_did, json.dumps({"hello":"world"}))
    print("created pairwise")

    await send_response(wallet_handle, did_str)


'''
    decrypts anoncrypted connection response
'''
async def handle_response(msg, wallet_handle):
    their_did = msg.did
    my_did = json.loads(await pairwise.get_pairwise(wallet_handle, their_did))['my_did']
    my_vk = await did.key_for_local_did(wallet_handle, my_did)

    decrypted_data = await crypto.anon_decrypt(my_vk, msg.data)
    print(decrypted_data)

'''
    sends a connection request.

    a connection response contains:
     - data concerning the request:
       - Name of Sender
       - Purpose

       - DID@A:B
       - URL of agent
       - Public verkey
'''
async def send_request(wallet_handle, owner):

    # get did and vk
    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")

    # get endpoint
    endpoint = input('Enter endpoint of receipient (http ip addresss):').strip()

    # make http request
    msg_json = json.dumps(
        {
            "type":"CONN_RES",
            "did" : my_did,
            "data": {
                "endpoint":endpoint,
                "owner": owner,
                "verkey": my_vk
            }
        }
    )

    # send to server
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=msg_json) as resp:
            print(resp.status)
            print(await resp.text())

'''
    sends a connection response should be anon_encrypted.

    a connection response will include:

    - user DID, and verkey
'''
async def send_response(wallet_handle, to_did):
    #find endpoint
    meta = json.loads(await did.get_did_metadata(wallet_handle, to_did))
    endpoint = meta['endpoint']
    print(endpoint)

    their_vk = await did.key_for_local_did(wallet_handle, to_did)
    print("Their Verkey: {}".format(their_vk))

    pairwise_json = json.loads(await pairwise.get_pairwise(wallet_handle, to_did))
    print(pairwise_json)
    my_did = pairwise_json['my_did']
    my_vk = await did.key_for_local_did(wallet_handle, my_did)
    print(my_vk)

    data = {
            'did': my_did,
            'verkey': my_vk
            }
    data = await crypto.anon_crypt(their_vk, json.dumps(data).encode('utf-8'))

    envelope = json.dumps({
            'type': 'CONN_RES',
            'did': my_did,
            'data': data
            })
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=envelope) as resp:
            print(resp.status)
            print(await resp.text())

