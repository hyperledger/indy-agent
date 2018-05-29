""" Message receiver handlers. """

# pylint: disable=import-error
from aiohttp import web

class MessageReceiver():
    """ Simple message queue interface for receiving messages.
    """
    def __init__(self, queue):
        self.msg_queue = queue

    async def handle_message(self, request):
        """ Put to message queue and return 202 to client.
        """
        msg = await request.read()
        await self.msg_queue.put(msg)
        raise web.HTTPAccepted()

    async def recv(self):
        """ Pop from message queue.
        """
        return await self.msg_queue.get()
