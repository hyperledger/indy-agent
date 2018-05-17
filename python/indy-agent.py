import asyncio
import os
import sys
import socket
from aiohttp import web
from aiohttp_index import IndexMiddleware
from indy import did, wallet, pool

from receiver.message_receiver import MessageReceiver as Receiver
from router.simple_router import SimpleRouter as Router

from model.agent import Agent
import modules.connection as connection
import modules.init as init
import serializer.json_serializer as Serializer

import jinja2
from aiohttp_index import IndexMiddleware
import aiohttp_jinja2
import view.site_handlers as site_handlers

if 'INDY_AGENT_PORT' in os.environ.keys():
    port = int(os.environ['INDY_AGENT_PORT'])
else:
    port = 8080

loop = asyncio.get_event_loop()
agent = web.Application(middlewares=[IndexMiddleware()])
agent['msg_router'] = Router()
agent['msg_receiver'] =  Receiver(asyncio.Queue())
agent['agent'] = Agent()

# template engine setup
aiohttp_jinja2.setup(agent,
    loader=jinja2.FileSystemLoader(os.path.realpath('view/templates/')))

routes = [
    web.get('/', site_handlers.index),
    web.post('/indy', agent['msg_receiver'].handle_message),
    web.post('/indy/init', init.initialize_agent),
    web.get('/indy/connections', connection.connections),
    web.get('/indy/requests', connection.requests),
]

agent.add_routes(routes)

runner = web.AppRunner(agent)
loop.run_until_complete(runner.setup())

server = web.TCPSite(runner, 'localhost', port)

async def message_process(agent):
    msg_router = agent['msg_router']
    msg_receiver = agent['msg_receiver']

    await msg_router.register("CONN_REQ", connection.handle_request_received)
    await msg_router.register("CONN_RES", connection.handle_response)
    print('===== Server Started on: http://localhost:{} ====='.format(port))
    while True:
        msg_bytes = await msg_receiver.recv()
        msg = Serializer.unpack(msg_bytes)
        await msg_router.route(msg, agent['agent'])

try:
    loop.create_task(server.start())
    loop.create_task(message_process(agent))
    loop.run_forever()
except KeyboardInterrupt:
    print("exiting")
