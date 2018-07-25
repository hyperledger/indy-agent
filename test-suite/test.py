""" indy-agent python implementation
"""

# Pylint struggles to find packages inside of a virtual environments;
# pylint: disable=import-error

# Pylint also dislikes the name indy-agent but this follows conventions already
# established in indy projects.
# pylint: disable=invalid-name

import asyncio
import os
import sys
import json
import uuid
from aiohttp import web

from indy import wallet, did, crypto

from transport.http_transport import HTTPTransport
import serializer.json_serializer as Serializer
from config import Config


# Configuration

DEFAULT_CONFIG_PATH = 'config.toml'

parser = Config.get_arg_parser()
config = Config.from_file(DEFAULT_CONFIG_PATH)

args = parser.parse_args()
if args:
    config.update(vars(args))

MSG_Q = asyncio.Queue()
TRANSPORT = HTTPTransport(config, MSG_Q)
# No router is needed for the test agent. (For now)
#ROUTER = Router()

# A router would be passed in here
async def run_tests(config, msg_q):
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

    # TODO: Run tests

    # TODO: Clean up


    #import sys
    #import unittest

    #sys.path[0:0] = ['.', '..', '../..']

    #SUITE = unittest.TestLoader().loadTestsFromNames(
    #    [
    #        'test_dataracebench',
    #        # 'test_instrumenter',
    #        # 'test_basic'
    #    ]
    #)
    #TESTRESULT = unittest.TextTestRunner(verbosity=1).run(SUITE)
    #sys.exit(0 if TESTRESULT.wasSuccessful() else 1)

    #for test_module in config.tests:


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

    #    try:
    #        msg = Serializer.unpack(msg_bytes)
    #    except Exception as e:
    #        print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
    #        continue

    #    await msg_router.route(msg, agent['agent'])

LOOP = asyncio.get_event_loop()
try:
    LOOP.create_task(TRANSPORT.start_server())
    LOOP.create_task(run_tests(config, MSG_Q))
    LOOP.run_forever()
except KeyboardInterrupt:
    print("exiting")
