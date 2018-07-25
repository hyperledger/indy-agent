import asyncio
from config import Config

class BaseTransport(object):
    def __init__(self, config: Config, message_queue: asyncio.Queue):
        self.config: Config = config
        self.message_queue: asyncio.Queue = message_queue

    async def start_server(self):
        """ The main task for the server aspect of transport.
        """
        pass

    async def send(self, dest: str, body: bytes):
        """ Send a message.
        """
        pass

    async def handle_message(self, msg: str):
        """ Push received message onto message queue.
        """
        await self.message_queue.put(msg)
