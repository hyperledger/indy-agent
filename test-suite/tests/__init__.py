""" Module containing Agent Test Suite Tests.
"""
import asyncio
import pytest
from typing import Callable

from config import Config

async def expect_message(message_queue: asyncio.Queue, timeout: int):
    get_message_task = asyncio.ensure_future(message_queue.get())
    sleep_task = asyncio.ensure_future(asyncio.sleep(timeout))
    finished, unfinished = await asyncio.wait(
        [
            get_message_task,
            sleep_task
        ],
        return_when=asyncio.FIRST_COMPLETED
    )
    print(finished)
    print(sleep_task)
    if get_message_task in finished:
        return get_message_task.result()

    for task in unfinished:
        task.cancel()

    pytest.fail("No message received before timing out")
