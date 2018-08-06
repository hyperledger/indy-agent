""" indy-agent python implementation
"""

import asyncio
import os
import json

from indy import wallet, did, crypto
from router import Router
from transport.http_transport import HTTPTransport
from serializer import JSONSerializer as Serializer
from config import Config

# Module Routes
from modules.testing import register_routes as testing_routes

# Configuration
DEFAULT_CONFIG_PATH = 'agent_config.toml'

parser = Config.get_arg_parser()
config = Config.from_file(DEFAULT_CONFIG_PATH)

args = parser.parse_args()
if args:
    config.update(vars(args))

# Transport and handling
TRANSPORT = HTTPTransport(config, asyncio.Queue())
ROUTER = Router()

async def message_process(config, transport, router):
    """ 
    """

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
    config.wallet_handle = await wallet.open_wallet(
        json.dumps({
            'id': config.wallet_name,
            'storage_config': {
                'path': config.wallet_path
            }
        }),
        json.dumps({'key': 'test-agent'})
    )

    await TRANSPORT.create_transport_key(config.wallet_handle)

    # Register Routes
    await testing_routes(router)

    while True:
        msg_bytes = await transport.recv()
        print('Got message: {}'.format(msg_bytes))
        try:
            msg = Serializer.unpack(msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
            continue

        await router.route(msg, config=config, transport=transport)

async def cleanup(config):
    if config.clear_wallets:
        await wallet.close_wallet(config.wallet_handle)
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

LOOP = asyncio.get_event_loop()
try:
    LOOP.create_task(TRANSPORT.start_server())
    LOOP.create_task(message_process(config, TRANSPORT, ROUTER))
    LOOP.run_forever()
except KeyboardInterrupt:
    print("exiting")

LOOP.run_until_complete(cleanup(config))
