import aiohttp_jinja2
import jinja2
import json
from indy import did, wallet

from router.simple_router import SimpleRouter
from model import Message, Agent
from message_types import ADMIN_WALLETCONNECTION
from . import Module

class AdminWalletConnection(Module):

    def __init__(self, agent):
        self.agent = agent
        self.router = SimpleRouter()
        self.router.register(ADMIN_WALLETCONNECTION.CONNECT, self.connect)

    async def route(self, msg: Message) -> Message:
        return await self.router.route(msg)

    async def connect(self, msg):
        """ Connect to existing wallet.
        """

        self.agent.owner = msg.name
        passphrase = msg.passphrase

        #set wallet name from msg contents
        wallet_name = '%s-wallet' % self.agent.owner

        wallet_config = json.dumps({"id": wallet_name})
        wallet_credentials = json.dumps({"key": passphrase})

        # pylint: disable=bare-except
        # TODO: better handle potential exceptions.
        try:
            await wallet.create_wallet(wallet_config, wallet_credentials)
        except Exception as e:
            print(e)

        try:
            self.agent.wallet_handle = await wallet.open_wallet(wallet_config,
                                                           wallet_credentials)
        except Exception as e:
            print(e)
            print("Could not open wallet!")

        (_, self.agent.endpoint_vk) = await did.create_and_store_my_did(
            self.agent.wallet_handle, "{}")

        self.agent.initialized = True
        # prompt a STATE message.
        return await self.agent.modules['ui'].ui_connect(None)
