import asyncio
import pytest
from message import Message
from tests import expect_message, validate_message, pack, unpack, sign_field, unpack_and_verify_signed_field
from indy import did
from . import Connection

@pytest.mark.asyncio
async def test_connection_started_by_tested_agent(config, wallet_handle, transport):
    invite_url = input('Input generated connection invite: ')

    invite_msg = Connection.Invite.parse(invite_url)

    print("\nReceived Invite:\n", invite_msg.pretty_print())

    # Create my information for connection
    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, '{}')

    # Send Connection Request to inviter
    request = Connection.Request.build(
        'test-connection-started-by-tested-agent',
        my_did,
        my_vk,
        config.endpoint
    )

    print("\nSending Request:\n", request.pretty_print())

    await transport.send(
        invite_msg['serviceEndpoint'],
        await pack(
            wallet_handle,
            my_vk,
            invite_msg['recipientKeys'][0],
            request
        )
    )

    # Wait for response
    print("Awaiting response from tested agent...")
    response_bytes = await expect_message(transport, 60)

    response = await unpack(
        wallet_handle,
        response_bytes,
        expected_to_vk=my_vk
    )

    Connection.Response.validate_pre_sig(response)
    print("\nReceived Response (pre signature verification):\n", response.pretty_print())

    response['connection'] = await unpack_and_verify_signed_field(response['connection~sig'])

    Connection.Response.validate(response)
    print("\nReceived Response (post signature verification):\n", response.pretty_print())

async def get_connection_started_by_suite(config, wallet_handle, transport, label=None):
    if label is None:
        label = 'test-suite'

    connection_key = await did.create_key(wallet_handle, '{}')

    invite_str = Connection.Invite.build(label, connection_key, config.endpoint)

    print("\n\nInvitation encoded as URL: ", invite_str)

    print("Awaiting request from tested agent...")
    request_bytes = await expect_message(transport, 90) # A little extra time to copy-pasta

    request = await unpack(
        wallet_handle,
        request_bytes,
        expected_to_vk=connection_key
    )

    Connection.Request.validate(request)
    print("\nReceived request:\n", request.pretty_print())

    (their_did, their_vk, their_endpoint) = Connection.Request.parse(request)

    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, '{}')

    response = Connection.Response.build(my_did, my_vk, config.endpoint)
    print("\nSending Response (pre signature packing):\n", response.pretty_print())

    response['connection~sig'] = await sign_field(wallet_handle, connection_key, response['connection'])
    del response['connection']
    print("\nSending Response (post signature packing):\n", response.pretty_print())

    await transport.send(
        their_endpoint,
        await pack(
            wallet_handle,
            my_vk,
            their_vk,
            response
        )
    )

    return {
        'my_did': my_did,
        'my_vk': my_vk,
        'their_did': their_did,
        'their_vk': their_vk,
        'their_endpoint': their_endpoint
    }

@pytest.mark.asyncio
async def test_connection_started_by_suite(config, wallet_handle, transport):
    await get_connection_started_by_suite(config, wallet_handle, transport, 'test-connection-started-by-suite')
