""" Asynchronous http server using aiohttp. """

import asyncio
from aiohttp import web

import view
from .base_receiver import BaseReceiver

class AioHttpReceiver(BaseReceiver):
    def __init__(self, queue):
        self.msg_queue = queue

    async def handle_message(self, request):
        view.require_init(request.app)

        msg = await request.read()
        await self.msg_queue.put(msg)
        raise web.HTTPAccepted()

    async def recv(self):
        return await self.msg_queue.get()
