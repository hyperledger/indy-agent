""" Module to handle the connection process.
"""

# pylint: disable=import-error

import json
import datetime
import aiohttp
from aiohttp import web
import aiohttp_jinja2
from indy import crypto, did, pairwise
import serializer.json_serializer as Serializer

async def handle_request_received(msg, agent):
    """ Handle reception of request, storing to be accepted later.
    """
    agent.received_requests[msg.did] = Serializer.pack(msg)


async def handle_response(msg, agent):
    """ Handle reception of connection response.

        Currently this relies on the did sent with the request being returned
        with the response as an identifier so we can decrypt the message.

        Relying on a nonce instead would be better.
    """
    wallet_handle = agent.wallet_handle

    # Get my did and verkey
    my_did = msg.did
    my_vk = await did.key_for_local_did(wallet_handle, my_did)

    # Anon Decrypt and decode the message
    decrypted_data = await crypto.anon_decrypt(wallet_handle, my_vk, msg.data)

    json_str = decrypted_data.decode("utf-8")
    resp_data = json.loads(json_str)

    # Get their did and vk and store in wallet
    their_did = resp_data["did"]
    their_vk = resp_data["verkey"]

    identity_json = json.dumps({
        "did": their_did,
        "verkey": their_vk
    })

    await did.store_their_did(wallet_handle, identity_json)
    #TODO: Do we want to store the metadata of owner and endpoint with their did?

    # Create pairwise identifier
    await pairwise.create_pairwise(
        wallet_handle,
        their_did,
        my_did,
        json.dumps({"test": "this is metadata"})
    )




async def handle_request_accepted(request):
    """ Handle reception of accept connection request message.
    """
    accept_did = request.match_info['did']
    agent = request.app['agent']
    wallet_handle = agent.wallet_handle

    if accept_did not in agent.received_requests:
        raise web.HTTPNotFound()

    msg = Serializer.unpack(agent.received_requests[accept_did])

    #TODO: validate correct format for incoming data
    data = msg.data
    endpoint = data['endpoint']
    verkey = data['verkey']
    owner = data['owner']

    ident_json = json.dumps(
        {
            "did": accept_did,
            "verkey": verkey
        }
    )

    meta_json = json.dumps(
        {
            "owner": owner,
            "endpoint": endpoint
        }
    )

    (my_did, _) = await did.create_and_store_my_did(wallet_handle, "{}")

    await did.store_their_did(wallet_handle, ident_json)

    await did.set_endpoint_for_did(wallet_handle, accept_did, endpoint, verkey)

    await did.set_did_metadata(wallet_handle, accept_did, meta_json)

    await pairwise.create_pairwise(wallet_handle, accept_did, my_did, json.dumps({"hello":"world"}))

    await send_response(accept_did, agent)

    raise web.HTTPFound('/')


@aiohttp_jinja2.template('index.html')
async def send_request(request):
    """ sends a connection request.

        a connection request contains:
         - data concerning the request:
           - Name of Sender
           - Purpose

           - DID@A:B
           - URL of agent
           - Public verkey
    """

    agent = request.app['agent']

    req_data = await request.post()

    our_endpoint = agent.endpoint
    endpoint = req_data['endpoint']
    wallet_handle = agent.wallet_handle
    owner = agent.owner


    # get did and vk
    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")

    # get endpoint


    # make http request
    msg_json = json.dumps(
        {
            "type": "CONN_REQ",
            "did": my_did,
            "data": {
                "endpoint": our_endpoint,
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
    print("Sending to {}".format(endpoint))
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=msg_json) as resp:
            print(resp.status)
            print(await resp.text())


    # Testing for webpage:
    conns = agent.connections
    reqs = agent.received_requests
    owner = agent.owner
    if owner is None or owner == '':
        owner = 'Default'
    return {
        "agent_name": owner,
        "connections": conns,
        "requests": reqs
    }



async def send_response(to_did, agent):
    """ sends a connection response should be anon_encrypted.

        a connection response will include:

        - user DID, and verkey
    """

    # find endpoint
    wallet_handle = agent.wallet_handle
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

    envelope = json.dumps(
        {
            'type': 'CONN_RES',
            'did': to_did,
            'data': data
        }
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=envelope) as resp:
            print(resp.status)
            print(await resp.text())
