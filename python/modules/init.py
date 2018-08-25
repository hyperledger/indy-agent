""" Handle agent initialization.
"""

# pylint: disable=import-error

import json

from indy import wallet, did

import modules.ui as ui


async def initialize_agent(msg, agent):
    """ Initialize agent.
    """
    data = msg.message
    agent.owner = data['name']
    passphrase = data['passphrase']
    wallet_config = json.dumps({"id": "wallet"})
    wallet_credentials = json.dumps({"key": "wallet_key"})

    wallet_name = '%s-wallet' % agent.owner

    # pylint: disable=bare-except
    # TODO: better handle potential exceptions.
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
    except Exception as e:
        print(e)

    try:
        agent.wallet_handle = await wallet.open_wallet(wallet_config,
                                                       wallet_credentials)
    except Exception as e:
        print(e)
        print("Could not open wallet!")

    (_, agent.endpoint_vk) = await did.create_and_store_my_did(
        agent.wallet_handle, "{}")

    agent.initialized = True
    return await ui.ui_connect(None, agent)
