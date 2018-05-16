import asyncio
import time
import re
import json
from indy import crypto, did, wallet

'''
    decrypts anoncrypted connection response 
'''
async def handle_response(self, data, wallet_handle):
    decrypted = await crypto.auth_decrypt(wallet_handle, my_vk, data)
    msg = decrypted.__getitem__(1).decode()
    print(msg)

'''
    Handles connection requests from other peers.
'''
async def handle_request(data, wallet_handle):
    #TODO: validate correct format for incoming data

    did_str = data['did']
    endpoint = data['endpoint']
    verkey = data['verkey']
    owner = data['owner']

    ident_json = json.dumps({
                             "did": did_str,
                             "verkey": verkey
                             })

    meta_json = json.dumps({
                            "owner": owner,
                            "endpoint": endpoint
                            })
    print(ident_json)

    await did.store_their_did(wallet_handle, ident_json)
    print("did and verkey stored")

    await did.set_endpoint_for_did(wallet_handle, did_str, endpoint, verkey)
    #print("endpoint stored")

    #print(meta_json)
    await did.set_did_metadata(wallet_handle, did_str, meta_json)
    print("meta_data stored")

    owner_key = await did.key_for_local_did(wallet_handle, did_str)
    print("owner's key: %s" % owner_key)



'''
    decrypts anoncrypted connection response
'''
def handle_response(data, wallet_handle):

    pass

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
def send_request(data, wallet_handle):
    # get your did, your verkey from wallet

    # get endpoint

    # get their endpoint

    # make http request

    # send to server

    pass

'''
    sends a connection response should be anon_encrypted. 
    
    a connection response will include: 
    
    - user DID, and verkey
'''
def send_response(data, wallet_handle):

    pass
