""" HTTP Transport
"""
import asyncio
import logging
from aiohttp import web, ClientSession

from config import Config
from . import BaseTransport

class HTTPTransport(BaseTransport):
    """ HTTP Transport
    """
    def __init__(self, config: Config, logger: logging.Logger, message_queue: asyncio.Queue):
        super().__init__(config, logger, message_queue)

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
        self.logger.info('Starting Server on: http://{}:{}'.format(self.config.host, self.config.port))
        await SERVER.start()

    async def send(self, dest: str, body: bytes):
        """ Send a message.
        """
        async with ClientSession() as session:
            async with session.post(dest, data=body) as resp:
                self.logger.debug("Response Status: {}".format(resp.status))
                self.logger.debug("Response text: {}".format(await resp.text()))

    async def handle_message(self, request: web.Request):
        """ Push received message onto message queue.
        """
        msg = await request.read()
        await self.message_queue.put(msg)
        raise web.HTTPAccepted()
