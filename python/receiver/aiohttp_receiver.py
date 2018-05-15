""" Asynchronous http server using aiohttp. """

import asyncio
from aiohttp import web
from .base_receiver import BaseReceiver

class AioHttpReceiver(BaseReceiver):
    def __init__(self, queue, port: int):
        self.port = port
        self.msg_queue = queue

    async def default_handler(self, request):
        msg = await request.read()
        await self.msg_queue.put(msg)
        print("Adding to queue")
        raise web.HTTPAccepted()

    def start(self, event_loop):
        server = web.Server(self.default_handler)
        print("======= Listening on http://127.0.0.1:8080/ ======")
        return event_loop.create_server(server, "127.0.0.1", self.port)

    async def recv(self):
        return await self.msg_queue.get()

if __name__ == "__main__":
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    receiver = AioHttpReceiver(q, 8080)

    async def consume():
        while True:
            msg = await receiver.recv()
            print(msg)

    try:
        producer_task = loop.create_task(receiver.start(loop))
        consumer_task = loop.create_task(consume())
        loop.run_forever()
    except KeyboardInterrupt:
        print("exiting")
