import asyncio
from receiver.aiohttp_receiver import AioHttpReceiver

q = asyncio.Queue()
loop = asyncio.get_event_loop()

receiver = AioHttpReceiver(q, 8080)

async def main():
    while True:
        msg = await receiver.recv()
        print(msg)

try:
    loop.create_task(receiver.start(loop))
    loop.create_task(main())
    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
