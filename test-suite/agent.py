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
DEFAULT_CONFIG_PATH = 'config.toml'

parser = Config.get_arg_parser()
config = Config.from_file(DEFAULT_CONFIG_PATH)

args = parser.parse_args()
if args:
    config.update(vars(args))

# Transport and handling
MSG_Q = asyncio.Queue()
TRANSPORT = HTTPTransport(config, MSG_Q)
ROUTER = Router()

async def message_process(config, msg_q, transport, router):
    """
    """

    # Initialization steps
    # -- Create wallet
    print('Creating wallet: {}'.format(config.wallet_name))
    try:
        await wallet.create_wallet(
            'pool1',
            config.wallet_name,
            None,
            None,
            json.dumps({'key': 'test-agent'})
        )
    except:
        pass

    # -- Open a wallet
    print('Opening wallet: {}'.format(config.wallet_name))
    config.wallet_handle = await wallet.open_wallet(
        config.wallet_name,
        None,
        json.dumps({'key': 'test-agent'})
    )

    # -- Create transport keys
    # create_key will create a verkey, sigkey keypair, store the sigkey in the wallet
    # and return the verkey.
    # The verkey is used to retrieve the sigkey from the wallet when needed.
    config.transport_key = await crypto.create_key(config.wallet_handle, '{}')

    # Register Routes
    await testing_routes(router)
    
    while True:
        msg_bytes = await msg_q.get()
        print('Got message: {}'.format(msg_bytes))
        try:
            msg = Serializer.unpack(msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
            continue

        await router.route(msg, config=config, message_queue=msg_q, transport=transport)

    #    encrypted_msg_bytes = await msg_receiver.recv()

    #    try:
    #        decrypted_msg_bytes = await crypto.anon_decrypt(
    #            agent.wallet_handle,
    #            agent.endpoint_vk,
    #            encrypted_msg_bytes
    #        )
    #    except Exception as e:
    #        print('Could not decrypt message: {}\nError: {}'.format(encrypted_msg_bytes, e))
    #        continue

LOOP = asyncio.get_event_loop()
try:
    LOOP.create_task(TRANSPORT.start_server())
    LOOP.create_task(message_process(config, MSG_Q, TRANSPORT, ROUTER))
    LOOP.run_forever()
except KeyboardInterrupt:
    print("exiting")
