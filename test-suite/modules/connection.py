""" Module to handle the connection process.
"""

# pylint: disable=import-error

import json
import uuid
import datetime
import aiohttp
from aiohttp import web
from indy import crypto, did, pairwise
from model import Message
import serializer.json_serializer as Serializer
from message_types import CONN, UI

async def send_offer(msg, agent):
    endpoint = msg.message['endpoint']
    name = msg.message['name']

    nonce = uuid.uuid4().hex
    agent.pending_offers[nonce] = name
    msg = Message(
        CONN.OFFER,
        nonce,
        {
            'name': name,
            'endpoint': {
                'url': agent.endpoint,
                'verkey': agent.endpoint_vk,
            }
        }
    )
    serialized_msg = Serializer.pack(msg)
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=serialized_msg) as resp:
            print(resp.status)
            print(await resp.text())

    return Message(UI.OFFER_SENT, nonce, {'name': name})

async def offer_recv(request):
    agent = request.app['agent']
    ui_event_queue = request.app['ui_event_queue']

    offer = Serializer.unpack(await request.read())
    agent.received_offers[offer.id] = offer

    # Notify UI
    offer_received_msg = Message(
        UI.OFFER_RECEIVED,
        offer.id,
        {'name': offer.message['name']}
    )
    await ui_event_queue.send(Serializer.pack(offer_received_msg))

    raise web.HTTPAccepted() # Return 202

async def handle_request(msg, agent):
    """ Handle reception of accept connection request message.
    """
    nonce = msg.id
    wallet_handle = agent.wallet_handle

    if nonce not in agent.pending_offers:
        return

    their_did = msg.message['did']
    their_vk = msg.message['verkey']

    ident_json = json.dumps(
        {
            "did": accept_did,
            "verkey": verkey
        }
    )

    meta_json = json.dumps(
        {
            "owner": owner,
            "endpoint": endpoint,
            "endpoint_vk": endpoint_vk
        }
    )

    (my_did, _) = await did.create_and_store_my_did(wallet_handle, "{}")

    await did.store_their_did(wallet_handle, ident_json)

    await did.set_endpoint_for_did(wallet_handle, accept_did, endpoint, verkey)

    await did.set_did_metadata(wallet_handle, accept_did, meta_json)

    await pairwise.create_pairwise(wallet_handle, accept_did, my_did, json.dumps({"hello":"world"}))

    await send_response(accept_did, agent)


async def send_request(offer, agent):
    """ sends a connection request.

        a connection request contains:
         - data concerning the request:
           - Name of Sender
           - Purpose

           - DID@A:B
           - URL of agent
           - Public verkey
    """

    conn_name = offer['name']
    our_endpoint = agent.endpoint
    endpoint_vk = offer['verkey']


    # get did and vk
    (my_did, my_vk) = await did.create_and_store_my_did(agent.wallet_handle, "{}")

    msg = Message(
        CONN.REQUEST,
        offer['nonce'],
        {
            'did': my_did,
            'verkey': my_vk,
            'endpoint': {
                'url': agent.endpoint,
                'verkey': agent.endpoint_vk,
            },

            #Extra Metadata
            'owner': agent.owner,
        }
    )
    serialized_msg = Serializer.pack(msg)

    # add to queue
    agent.connections[my_did] = {
        "name": offer['name'],
        "endpoint": offer['endpoint'],
        "time": str(datetime.datetime.now()).split(' ')[1].split('.')[0],
        "status": "pending"
    }

    # send to server
    print("Sending to {}".format(offer['endpoint']))
    async with aiohttp.ClientSession() as session:
        async with session.post(offer['endpoint'], data=serialized_msg) as resp:
            print(resp.status)
            print(await resp.text())

    return {'type': 'CONN_REQ_SENT', 'id': None, 'data': agent.connections[my_did]}


async def handle_response(msg, agent):
    """ Handle reception of connection response.

        Currently this relies on the did sent with the request being returned
        with the response as an identifier so we can decrypt the message.

        Relying on a nonce instead would be better.
    """
    wallet_handle = agent.wallet_handle

    # Get my did and verkey
    my_did = msg.id
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



async def send_response(to_did, agent):
    """ sends a connection response should be anon_encrypted.

        a connection response will include:

        - user DID, and verkey
    """

    # find endpoint
    wallet_handle = agent.wallet_handle
    meta = json.loads(await did.get_did_metadata(wallet_handle, to_did))
    endpoint = meta['endpoint']
    endpoint_vk = meta['endpoint_vk']

    their_vk = await did.key_for_local_did(wallet_handle, to_did)

    pairwise_json = json.loads(await pairwise.get_pairwise(wallet_handle, to_did))
    my_did = pairwise_json['my_did']
    my_vk = await did.key_for_local_did(wallet_handle, my_did)

    data = {
        'did': my_did,
        'verkey': my_vk
    }

    data = await crypto.anon_crypt(their_vk, json.dumps(data).encode('utf-8'))

    envelope = json.dumps(
        {
            'type': 'CONN_RES',
            'id': to_did,
            'data': data
        }
    )

    encrypted_envelope = await crypto.anon_crypt(endpoint_vk, Serializer.pack(envelope))

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=envelope) as resp:
            print(resp.status)
            print(await resp.text())
