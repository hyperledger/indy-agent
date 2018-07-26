import asyncio
import pytest
from . import expect_message

@pytest.mark.asyncio
async def test_got_hello_world(config, transport, msg_q):
    msg = await expect_message(msg_q, 60)
    assert msg.decode('utf-8') == 'Hello, world!'
