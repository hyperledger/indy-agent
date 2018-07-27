import asyncio
import pytest
from modules.testing import SendMessageCommand
from serializer import JSONSerializer as Serializer
from . import expect_message

@pytest.mark.asyncio
async def test_got_hello_world(config, transport, msg_q):
    send_msg_cmd = SendMessageCommand(
        'http://localhost:3000/indy',
        {
            'type': 'hello_world',
            'message': 'Hello, world!'
        }
    )
    await transport.send(config.tested_agent, Serializer.pack(send_msg_cmd))
    msg_bytes = await expect_message(msg_q, 5)
    msg = Serializer.unpack(msg_bytes)

    assert msg.type == 'hello_world'
    assert msg.vars['message'] == 'Hello, world!'
