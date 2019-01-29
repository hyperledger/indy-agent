import asyncio
import pytest
from message import Message
from modules.testing import MESSAGE_TYPES as TESTING_MESSAGE
from serializer import JSONSerializer as Serializer
from tests import expect_message

@pytest.mark.asyncio
async def test_got_ttt_res(emailTransport):
    await emailTransport.demo()
    msg_bytes = await expect_message(emailTransport, 5)
    msg = Serializer.unpack(msg_bytes)

    assert msg.type == 'hello_world'
    assert msg.message == 'Hello, world!'
