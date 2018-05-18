import asyncio
import time
import re
import json
import datetime
import aiohttp
from aiohttp import web
import aiohttp_jinja2
from indy import crypto, did, wallet, pairwise
from modules import init

'''
    decrypts anoncrypted connection response
'''
#async def handle_response(self, data, wallet_handle):
#    decrypted = await crypto.auth_decrypt(wallet_handle, my_vk, data)
#    msg = decrypted.__getitem__(1).decode()
#    print(msg)


async def handle_request_received(msg, agent):
    agent.received_requests[msg.did] = msg


async def handle_response(msg, agent):
    """
        decrypts anoncrypted connection response
    """
    wallet_handle = agent['wallet_handle']
    their_did = msg.did
    my_did = json.loads(await pairwise.get_pairwise(wallet_handle, their_did))['my_did']
    my_vk = await did.key_for_local_did(wallet_handle, my_did)

    decrypted_data = await crypto.anon_decrypt(my_vk, msg.data)
    print(decrypted_data)


async def handle_request_accepted(request):
    """ From web router.
    """
    accepted_data = json.loads(await request.read())
    agent = request.app['agent']
    wallet_handle = agent.wallet_handle
    did_str = accepted_data['did']

    if did_str not in agent.received_requests:
        return
    if not accepted_data['accepted']:
        agent.received_requests.pop(did_str)

    msg = agent.received_requests[did_str]

    #TODO: validate correct format for incoming data
    data = msg.data
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

    # await send_response(wallet_handle, did_str)


@aiohttp_jinja2.template('index.html')
async def send_request(request):

    """
        sends a connection request.

        a connection response contains:
         - data concerning the request:
           - Name of Sender
           - Purpose

           - DID@A:B
           - URL of agent
           - Public verkey
    """
    await init.initialize_agent(request)
    agent = request.app['agent']

    req_data = await request.post()

    me = req_data['agent_name']
    agent.me = me
    endpoint = req_data['endpoint']
    wallet_handle = agent.wallet_handle
    owner = agent.me


    # get did and vk
    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")

    # get endpoint


    # make http request
    msg_json = json.dumps(
        {
            "type": "CONN_RES",
            "did": my_did,
            "data": {
                "endpoint": endpoint,
                "owner": owner,
                "verkey": my_vk
            }
        }
    )

    # add to queue
    agent.connections[endpoint] = {
        "endpoint": endpoint,
        "time": str(datetime.datetime.now()).split(' ')[1].split('.')[0],
        "status": "pending"
    }

    # send to server
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=msg_json) as resp:
            print(resp.status)
            print(await resp.text())


    # Testing for webpage:
    conns = agent.connections
    reqs = agent.received_requests
    me = agent.me
    if me is None or me == '':
        me = 'Default'
    return {
        "agent_name": me,
        "connections": conns,
        "requests": reqs
    }



async def send_response(wallet_handle, to_did):
    """
        sends a connection response should be anon_encrypted.

        a connection response will include:

        - user DID, and verkey
    """

    # find endpoint
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

