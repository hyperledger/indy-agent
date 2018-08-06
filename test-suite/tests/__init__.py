""" Module containing Agent Test Suite Tests.
"""
import asyncio
import pytest
from typing import Callable

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

    pytest.fail("No message received before timing out")
