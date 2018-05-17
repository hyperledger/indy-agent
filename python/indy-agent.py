import asyncio
import os
import sys
from aiohttp import web
from indy import did, wallet, pool

import view
from receiver.aiohttp_receiver import AioHttpReceiver as Receiver
from router.simple_router import SimpleRouter as Router
import modules.connection as connection
import serializer.json_serializer as Serializer
from aiohttp_index import IndexMiddleware

if 'INDY_AGENT_PORT' in os.environ.keys():
    port = int(os.environ['INDY_AGENT_PORT'])
else:
    port = 8080

loop = asyncio.get_event_loop()
agent = web.Application(middlewares=[IndexMiddleware()])
agent['msg_router'] = Router()
agent['msg_receiver'] =  Receiver(asyncio.Queue())
agent['initialized'] = False

routes = [
    web.static('/', os.path.realpath('view/')),
    web.post('/indy', agent['msg_receiver'].handle_message),
    web.post('/indy/init', view.init)
]

agent.add_routes(routes)

runner = web.AppRunner(agent)
loop.run_until_complete(runner.setup())

server = web.TCPSite(runner, 'localhost', port)

async def main(agent):
    msg_router = agent['msg_router']
    msg_receiver = agent['msg_receiver']

    await msg_router.register("CONN_REQ", connection.handle_request)
    await msg_router.register("CONN_RES", connection.handle_response)

    while True:
        msg_bytes = await msg_receiver.recv()
        msg = Serializer.unpack(msg_bytes)
        await msg_router.route(msg, agent['wallet_handle'])

try:
    loop.create_task(server.start())
    loop.create_task(main(agent))
    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
