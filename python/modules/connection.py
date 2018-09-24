""" Module to handle the connection process.
"""

# pylint: disable=import-error

import json
import base64
import aiohttp
from indy import crypto, did

import serializer.json_serializer as Serializer
from model import Message
from message_types import UI_NEW, CONN_NEW
from helpers import serialize_bytes_json, bytes_to_str, str_to_bytes


async def send_invite(msg: Message, agent) -> Message:
    receiver_endpoint = msg.content['endpoint']
    conn_name = msg.content['name']

    msg = Message(
        type=CONN_NEW.SEND_INVITE,
        content={
            'name': conn_name,
            'endpoint': {
                'url': agent.endpoint,
                'verkey': agent.endpoint_vk,
            },
        }
    )
    serialized_msg = Serializer.pack(msg)
    async with aiohttp.ClientSession() as session:
        async with session.post(receiver_endpoint, data=serialized_msg) as resp:
            print(resp.status)
            print(await resp.text())

    return Message(
        type=UI_NEW.INVITE_SENT,
        id=agent.ui_token,
        content={'name': conn_name})


async def invite_received(msg: Message, agent) -> Message:
    conn_name = msg.content['name']

    return Message(
        type=UI_NEW.INVITE_RECEIVED,
        content={'name': conn_name,
                 'endpoint': msg.content['endpoint'],
                 'history': msg}
    )


async def send_request(msg: Message, agent) -> Message:
    their_endpoint = msg.content['endpoint']
    conn_name = msg.content['name']
    connection_key = msg.content['key']

    my_endpoint_uri = agent.endpoint

    (endpoint_did_str, endpoint_key) = await did.create_and_store_my_did(agent.wallet_handle, "{}")

    #  workaround to pass conn_name securely back to the invite sender, otherwise we could just send the did
    data_to_send = json.dumps(
        {
            "did": endpoint_did_str,
            "conn_name": conn_name
        }
    )

    endpoint_did_bytes = str_to_bytes(data_to_send)

    meta_json = json.dumps(
        {
            "conn_name": conn_name
        }
    )

    await did.set_did_metadata(agent.wallet_handle, endpoint_did_str, meta_json)

    inner_msg = Message(
        type= "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",
        key= agent.endpoint_vk,
        endpoint= my_endpoint_uri,
        content= serialize_bytes_json(await crypto.auth_crypt(agent.wallet_handle, endpoint_key, connection_key, endpoint_did_bytes))
    )

    outer_msg = Message(
        type='did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward_to_key',
        key=agent.endpoint_vk,
        content=inner_msg
    )

    serialized_outer_msg = Serializer.pack(outer_msg)

    serialized_outer_msg_bytes = str_to_bytes(serialized_outer_msg)

    all_message = Message(
        type=CONN_NEW.SEND_REQUEST,
        content=serialize_bytes_json(
            await crypto.anon_crypt(connection_key,
                                    serialized_outer_msg_bytes))
    )

    serialized_msg = Serializer.pack(all_message)

    async with aiohttp.ClientSession() as session:
        async with session.post(their_endpoint, data=serialized_msg) as resp:
            print(resp.status)
            print(await resp.text())

    return Message(
        type=UI_NEW.REQUEST_SENT,
        id=agent.ui_token,
        content={'name': conn_name}
    )


async def request_received(msg: Message, agent) -> Message:
    sender_endpoint_uri = msg.endpoint
    endpoint_key = msg.key

    message_bytes = msg.content.encode('utf-8')
    message_bytes = base64.b64decode(message_bytes)

    sender_key_str, sender_data_bytes = await crypto.auth_decrypt(
        agent.wallet_handle, agent.endpoint_vk, message_bytes)

    sender_data_json = json.loads(sender_data_bytes.decode('utf-8'))

    sender_did_str = sender_data_json['did']
    conn_name = sender_data_json['conn_name']

    identity_json = json.dumps(
        {
            "did": sender_did_str,
            # TODO: we don't use verkey later
            "verkey": sender_key_str
        }
    )

    await did.store_their_did(agent.wallet_handle, identity_json)

    meta_json = json.dumps(
        {
            "conn_name": conn_name
        }
    )

    await did.set_did_metadata(agent.wallet_handle, sender_did_str, meta_json)

    return Message(
        type=UI_NEW.REQUEST_RECEIVED,
        content={
            'name': conn_name,
            'endpoint_uri': sender_endpoint_uri,
            'endpoint_key': endpoint_key,
            'endpoint_did': sender_did_str,
            'history': msg
        }
    )


async def send_response(msg: Message, agent) -> Message:
    receiver_endpoint_uri = msg.content['endpoint_uri']
    receiver_endpoint_key = msg.content['endpoint_key']
    receiver_endpoint_did = msg.content['endpoint_did']
    receiver_endpoint_did_bytes = str_to_bytes(receiver_endpoint_did)

    inner_msg = Message(
        type="did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/response",
        to="did:sov:ABC",
        content=serialize_bytes_json(await crypto.auth_crypt(agent.wallet_handle, agent.endpoint_vk, receiver_endpoint_key, receiver_endpoint_did_bytes))
    )

    outer_msg = Message(
        type="did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward",
        to="ABC",
        content=inner_msg
    )

    serialized_outer_msg = Serializer.pack(outer_msg)

    serialized_outer_msg_bytes = str_to_bytes(serialized_outer_msg)

    all_message = Message(
        content=serialize_bytes_json(await crypto.anon_crypt(receiver_endpoint_key,
                                                             serialized_outer_msg_bytes))
    )

    serialized_msg = Serializer.pack(all_message)

    async with aiohttp.ClientSession() as session:
        async with session.post(receiver_endpoint_uri, data=serialized_msg) as resp:
            print(resp.status)
            print(await resp.text())

    meta = json.loads(await did.get_did_metadata(agent.wallet_handle,
                                                 receiver_endpoint_did))
    conn_name = meta['conn_name']

    return Message(type=UI_NEW.RESPONSE_SENT,
                   id=agent.ui_token,
                   content={'name': conn_name})


async def response_received(msg: Message, agent) -> Message:
    message_bytes = msg.content.encode('utf-8')
    message_bytes = base64.b64decode(message_bytes)

    sender_key_str, sender_did_bytes = await crypto.auth_decrypt(agent.wallet_handle, agent.endpoint_vk, message_bytes)

    sender_did_str = bytes_to_str(sender_did_bytes)
    meta = json.loads(await did.get_did_metadata(agent.wallet_handle,
                                                 sender_did_str))
    conn_name = meta['conn_name']

    return Message(
        type=UI_NEW.RESPONSE_RECEIVED,
        id=agent.ui_token,
        content={'name': conn_name,
                 'history': msg}
    )


