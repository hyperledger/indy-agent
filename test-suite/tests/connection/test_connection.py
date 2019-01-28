import asyncio
import pytest
import re
import base64
from message import Message
from serializer import JSONSerializer as Serializer
from tests import expect_message, validate_message, pack, unpack
from indy import did

class Connection:

    FAMILY_NAME = "connections"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    INVITE = FAMILY + "invite"
    REQUEST = FAMILY + "request"
    RESPONSE = FAMILY + "response"

@pytest.mark.asyncio
async def test_connection_started_by_tested_agent(config, wallet_handle, transport):
    invite_url = input('Input generated connection invite: ')

    matches = re.match('(.+)?c_i=(.+)', invite_url)
    assert matches, 'Improperly formatted invite url!'

    invite_msg = Serializer.unpack(
        base64.urlsafe_b64decode(matches.group(2)).decode('utf-8')
    )

    validate_message(
        [
            '@type',
            'label',
            'key',
            'endpoint'
        ],
        invite_msg
    )

    # Create my information for connection
    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, '{}')


    # Send Connection Request to inviter
    request = Message({
        '@type': Connection.REQUEST,
        'label': 'testing-agent',
        'DID': my_did,
        'DIDDoc': {
            'key': my_vk,
            'endpoint': config.endpoint,
        }
    })

    await transport.send(invite_msg['endpoint'], await pack(wallet_handle, my_vk, invite_msg['key'], request))

    # Wait for response
    response_bytes = await expect_message(transport, 60)

    response = await unpack(wallet_handle, response_bytes, expected_to_vk=my_vk)

    validate_message(
        [
            '@type',
            'DID',
            'DIDDoc'
        ],
        response
    )

    validate_message(
        [
            'key',
            'endpoint'
        ],
        response['DIDDoc']
    )
