import asyncio
import pytest

@pytest.mark.asyncio
async def test_one(config, transport):
    print('Hello from test one!')
    print(config)

@pytest.mark.asyncio
async def test_two(config):
    print('Hello from test two!')
    print(config)
