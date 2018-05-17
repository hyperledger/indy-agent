""" Message receiver handlers. """

import asyncio
from aiohttp import web

import web_utils as utils

class MessageReceiver():
    def __init__(self, queue):
        self.msg_queue = queue

    async def handle_message(self, request):
        utils.require_init(request.app['agent'])

        msg = await request.read()
        await self.msg_queue.put(msg)
        raise web.HTTPAccepted()

    async def recv(self):
        return await self.msg_queue.get()
