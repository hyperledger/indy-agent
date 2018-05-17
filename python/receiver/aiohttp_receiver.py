""" Asynchronous http server using aiohttp. """

import asyncio
from aiohttp import web
from .base_receiver import BaseReceiver

class AioHttpReceiver(BaseReceiver):
    def __init__(self, queue):
        self.msg_queue = queue

    async def handle_message(self, request):
        if request.method != "POST":
            raise web.HTTPMethodNotAllowed(request.method, "POST")
        msg = await request.read()
        await self.msg_queue.put(msg)
        print("Adding to queue")
        raise web.HTTPAccepted()

    async def recv(self):
        return await self.msg_queue.get()
