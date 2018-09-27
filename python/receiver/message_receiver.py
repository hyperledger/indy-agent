""" Message receiver handlers. """

# pylint: disable=import-error
from aiohttp import web
import asyncio

class MessageReceiver():
    """ Simple message queue interface for receiving messages.
    """
    def __init__(self):
        self.msg_queue = asyncio.Queue()

    async def handle_message(self, request):
        """ Put to message queue and return 202 to client.
        """
        if not request.app['agent'].initialized:
            raise web.HTTPUnauthorized()

        msg = await request.read()
        await self.msg_queue.put(msg)
        raise web.HTTPAccepted()

    async def recv(self):
        """ Pop from message queue.
        """
        return await self.msg_queue.get()
