import pytest
import asyncio
import json
from indy import crypto, wallet
from config import Config
from transport.http_transport import HTTPTransport

@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()

@pytest.fixture(scope='session')
async def config():
    DEFAULT_CONFIG_PATH = 'config.toml'

    config = Config.from_file(DEFAULT_CONFIG_PATH)
    #parser = Config.get_arg_parser()

    #args = parser.parse_args()
    #if args:
    #    config.update(vars(args))

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

    return config

@pytest.fixture(scope='session')
def msg_q():
    return asyncio.Queue()

@pytest.fixture(scope='session')
def transport(config, msg_q, event_loop):
    transport = HTTPTransport(config, msg_q)
    event_loop.run_until_complete(transport.start_server())
    return transport
