""" HTTP Transport
"""
import asyncio
from aiohttp import web, ClientSession

from config import Config
from . import BaseTransport

class HTTPTransport(BaseTransport):
    """ HTTP Transport
    """
    def __init__(self, config: Config, message_queue: asyncio.Queue):
        super().__init__(config, message_queue)

    async def start_server(self):
        """ The main task for the server aspect of transport.
        """
        APP = web.Application()
        ROUTES = [
            web.post('/indy', self.handle_message)
        ]
        APP.add_routes(ROUTES)
        RUNNER = web.AppRunner(APP)
        await RUNNER.setup()
        SERVER = web.TCPSite(RUNNER, self.config.host, self.config.port)
        print('===== Starting Server on: http://{}:{} ====='.format(self.config.host, self.config.port))
        await SERVER.start()

    async def send(self, dest: str, body: bytes):
        """ Send a message.
        """
        async with ClientSession() as session:
            async with session.post(dest, data=body) as resp:
                print(resp.status)
                print(await resp.text())

    async def handle_message(self, request: web.Request):
        """ Push received message onto message queue.
        """
        msg = await request.read()
        await self.message_queue.put(msg)
        raise web.HTTPAccepted()
