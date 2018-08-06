""" Test Suite fixture definitions.

    These fixtures define the core functionality of the testing agent.

    For more information on how pytest fixtures work, see
    https://docs.pytest.org/en/latest/fixture.html#fixture
"""

import pytest
import asyncio
import json
import os
from indy import crypto, wallet
from config import Config
from transport.http_transport import HTTPTransport

@pytest.fixture(scope='session')
def event_loop():
    """ Create a session scoped event loop.

        pytest.asyncio plugin provides a default function scoped event loop
        which cannot be used as a dependency to session scoped fixtures.
    """
    return asyncio.get_event_loop()

@pytest.fixture(scope='session')
async def config():
    """ Gather configuration and initialize the wallet.
    """
    DEFAULT_CONFIG_PATH = 'test_config.toml'

    config = Config.from_file(DEFAULT_CONFIG_PATH)
    parser = Config.get_arg_parser()

    args = parser.parse_args()
    if args:
        config.update(vars(args))

    yield config

    # TODO: Cleanup?


@pytest.fixture(scope='session')
async def wallet_handle(config):
    # Initialization steps
    # -- Create wallet
    print('Creating wallet: {}'.format(config.wallet_name))
    try:
        await wallet.create_wallet(
            json.dumps({
                'id': config.wallet_name,
                'storage_config': {
                    'path': config.wallet_path
                }
            }),
            json.dumps({'key': 'test-agent'})
        )
    except:
        pass

    # -- Open a wallet
    print('Opening wallet: {}'.format(config.wallet_name))
    wallet_handle = await wallet.open_wallet(
        json.dumps({
            'id': config.wallet_name,
            'storage_config': {
                'path': config.wallet_path
            }
        }),
        json.dumps({'key': 'test-agent'})
    )

    yield wallet_handle

    # Cleanup
    if config.clear_wallets:
        await wallet.close_wallet(wallet_handle)
        await wallet.delete_wallet(
            json.dumps({
                'id': config.wallet_name,
                'storage_config': {
                    'path': config.wallet_path
                }
            }),
            json.dumps({'key': 'test-agent'})
        )

        os.rmdir(config.wallet_path)


@pytest.fixture(scope='session')
async def transport(config, wallet_handle, event_loop):
    """ Transport fixture.

        Initializes the transport layer.
    """
    MSG_Q = asyncio.Queue()
    transport = HTTPTransport(config, MSG_Q)

    await transport.create_transport_key(wallet_handle)

    event_loop.create_task(transport.start_server())
    return transport
