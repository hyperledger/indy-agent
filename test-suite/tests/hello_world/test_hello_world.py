import asyncio
import pytest
from message import Message
from modules.testing import MESSAGE_TYPES as TESTING_MESSAGE
from serializer import JSONSerializer as Serializer
from tests import expect_message

@pytest.mark.asyncio
async def test_got_hello_world(config, transport):
    msg = Message({
        'type': TESTING_MESSAGE.SEND_MESSAGE,
        'to': 'http://localhost:3000/indy',
        'content': {
            'type': 'hello_world',
            'message': 'Hello, world!'
        }
    })

    await transport.send(config.tested_agent, Serializer.pack(msg))
    msg_bytes = await expect_message(transport, 5)
    msg = Serializer.unpack(msg_bytes)

    assert msg.type == 'hello_world'
    assert msg.message == 'Hello, world!'
