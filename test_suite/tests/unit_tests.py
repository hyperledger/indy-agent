import pytest
import asyncio
from indy import crypto
from tests import sign_field, unpack_and_verify_signed_field

@pytest.mark.asyncio
async def test_can_sign_and_verify(config, wallet_handle):
    msg = {"test": "test"}
    my_key = await crypto.create_key(wallet_handle, '{}')
    signed_field = await sign_field(wallet_handle, my_key, msg)
    assert await unpack_and_verify_signed_field(signed_field)
