""" Module containing Agent Test Suite Tests.
"""
import base64
import json
import time
import struct
import asyncio
import pytest
from pytest import fail
from typing import Callable, Any
from indy import crypto

from message import Message
from serializer import JSONSerializer as Serializer
from transport import BaseTransport

async def expect_message(transport: BaseTransport, timeout: int):
    get_message_task = asyncio.ensure_future(transport.recv())
    sleep_task = asyncio.ensure_future(asyncio.sleep(timeout))
    finished, unfinished = await asyncio.wait(
        [
            get_message_task,
            sleep_task
        ],
        return_when=asyncio.FIRST_COMPLETED
    )
    if get_message_task in finished:
        return get_message_task.result()

    for task in unfinished:
        task.cancel()

    fail("No message received before timing out; tested agent failed to respond")

def validate_message(expected_attrs: [Any], msg: Message):
    __tracebackhide__ = True
    for attribute in expected_attrs:
        if isinstance(attribute, tuple):
            assert attribute[0] in msg, \
                'Attribute "{}" is missing from message: \n{}'.format(attribute[0], msg)
            assert msg[attribute[0]] == attribute[1], \
                'Message.{}: {} != {}'.format(attribute[0], msg[attribute[0]], attribute[1])
        else:
            assert attribute in msg, \
                'Attribute "{}" is missing from message: \n{}'.format(attribute, msg)

async def pack(wallet_handle: int, my_vk: str, their_vk: str, msg: Message) -> bytes:
    return await crypto.pack_message(
        wallet_handle,
        Serializer.pack(msg),
        [their_vk],
        my_vk
    )

async def unpack(wallet_handle: int, wire_msg_bytes: bytes, **kwargs) -> Message:
    __tracebackhide__ = True

    wire_msg = json.loads(
        await crypto.unpack_message(
            wallet_handle,
            wire_msg_bytes
        )
    )

    if 'expected_to_vk' in kwargs:
        assert kwargs['expected_to_vk'] == wire_msg['recipient_verkey'], \
            'Message is not for the expected verkey!'

    if 'expected_from_vk' in kwargs:
        assert kwargs['expected_from_vk'] == wire_msg['sender_verkey'], \
            'Message is not from the expected verkey!'

    return Serializer.unpack(wire_msg['message'])

async def unpack_and_verify_signed_field(signed_field):
    signature_bytes = base64.urlsafe_b64decode(signed_field['signature'].encode('utf-8'))
    assert await crypto.crypto_verify(
        signed_field['signer'],
        signed_field['sig_data'],
        signature_bytes
    ), "Signature verification failed on field {}!".format(signed_field)
    data_bytes = base64.urlsafe_b64decode(signed_field['sig_data'])
    timestamp = struct.unpack(">Q", data_bytes[:8])
    fieldjson = data_bytes[8:]
    return json.loads(fieldjson)

async def sign_field(wallet_handle, my_vk, field_value):
    timestamp_bytes = struct.pack(">Q", int(time.time()))

    sig_data = base64.urlsafe_b64encode(
        timestamp_bytes + json.dumps(field_value).encode()
    ).decode('utf-8')

    signature = base64.urlsafe_b64encode(
        await crypto.crypto_sign(
            wallet_handle,
            my_vk,
            sig_data
        )
    ).decode('utf-8')

    return {
        "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/signature/1.0/ed25519Sha512_single",
        "sig_data": sig_data,
        "signer": my_vk,
        "signature": signature
    }
