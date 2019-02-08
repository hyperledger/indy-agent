""" Wrappers around Indy-SDK functions to overcome shortcomings in the SDK.
"""
import json
from indy import did, crypto, non_secrets, error

async def create_and_store_my_did(wallet_handle):
    """ Create and store my DID, adding a map from verkey to DID using the
        non_secrets API.
    """
    (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, '{}')

    await non_secrets.add_wallet_record(
        wallet_handle,
        'key-to-did',
        my_vk,
        my_did,
        '{}'
    )

    return (my_did, my_vk)

async def store_their_did(wallet_handle, their_did, their_vk):
    """ Store their did, adding a map from verkey to DID using the non_secrets
        API.
    """
    await did.store_their_did(
        wallet_handle,
        json.dumps({
            'did': their_did,
            'verkey': their_vk,
        })
    )

    await non_secrets.add_wallet_record(
        wallet_handle,
        'key-to-did',
        their_vk,
        their_did,
        '{}'
    )


async def did_for_key(wallet_handle, key):
    """ Retrieve DID for a given key from the non_secrets verkey to DID map.
    """
    did = None
    try:
        did = json.loads(
            await non_secrets.get_wallet_record(
                wallet_handle,
                'key-to-did',
                key,
                '{}'
            )
        )['value']
    except error.IndyError as e:
        if e.error_code is error.ErrorCode.WalletItemNotFound:
            pass
        else:
            raise e

    return did
