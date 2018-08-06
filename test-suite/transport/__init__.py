import asyncio
from indy import crypto
from config import Config

class BaseTransport(object):
    def __init__(self, config: Config, message_queue: asyncio.Queue):
        self.config: Config = config
        self.message_queue: asyncio.Queue = message_queue
        self.verkey = None

    async def start_server(self):
        """ The main task for the server aspect of transport.
        """
        pass

    async def create_transport_key(self, wallet_handle: int):
        """ Create transport keys

            create_key will create a verkey, sigkey keypair, store the sigkey in the wallet
            and return the verkey.
            The verkey is used to retrieve the sigkey from the wallet when needed.
        """
        self.verkey = await crypto.create_key(wallet_handle, '{}')

    async def send(self, dest: str, body: bytes):
        """ Send a message.
        """
        pass

    async def recv(self):
        return await self.message_queue.get()

    async def handle_message(self, msg: str):
        """ Push received message onto message queue.
        """
        await self.message_queue.put(msg)
