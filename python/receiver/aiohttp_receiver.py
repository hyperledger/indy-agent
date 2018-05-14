""" Asynchronous http server using aiohttp. """

import asyncio
from aiohttp import web
from base_receiver import BaseReceiver

class AioHttpReceiver(BaseReceiver):
    def __init__(self, queue, port: int):
        self.port = port
        self.msg_queue = queue

    async def default_handler(request):
        msg = await request.read()
        self.msg_queue.put(msg)
        print("Adding to queue")
        raise web.HTTPAccepted()

    async def start(self, event_loop, handler=default_handler):
        server = web.Server(handler)
        await loop.create_server(server, "127.0.0.1", 8080)
        print("======= Serving on http://127.0.0.1:8080/ ======")
        await asyncio.sleep(100*3600)

if __name__ == "__main__":
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    receiver = AioHttpReceiver(q, 8080)
    loop.run_until_complete(receiver.start(loop))
