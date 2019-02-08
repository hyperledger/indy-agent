""" Module containing Agent Test Suite Tests.
"""
import base64
import json
import asyncio
import pytest
from pytest import fail
from typing import Callable
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

def validate_message(expected_attrs: [str], msg: Message):
    __tracebackhide__ = True
    for attribute in expected_attrs:
        if attribute not in msg:
            fail("Attribute \"{}\" is missing from msg:\n{}".format(attribute, msg))

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
        assert kwargs['expected_to_vk'] == wire_msg['recipient_verkey'], 'Message is not for the expected verkey!'

    if 'expected_from_vk' in kwargs:
        assert kwargs['expected_from_vk'] == wire_msg['sender_verkey'], 'Message is not from the expected verkey!'

    return Serializer.unpack(wire_msg['message'])
