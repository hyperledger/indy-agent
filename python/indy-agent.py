""" indy-agent python implementation
"""

# Pylint struggles to find packages inside of a virtual environments;
# pylint: disable=import-error

# Pylint also dislikes the name indy-agent but this follows conventions already
# established in indy projects.
# pylint: disable=invalid-name

import asyncio
import os
import sys
import json
from aiohttp import web
from aiohttp_index import IndexMiddleware
import jinja2
import aiohttp_jinja2

from receiver.message_receiver import MessageReceiver as Receiver
from router.simple_router import SimpleRouter as Router
from ui_event import UIEventQueue
from model import Agent
import modules.connection as connection
import modules.init as init
import modules.ui as ui
import serializer.json_serializer as Serializer
import view.site_handlers as site_handlers

if len(sys.argv) == 2 and str.isdigit(sys.argv[1]):
    PORT = int(sys.argv[1])
else:
    PORT = 8080

LOOP = asyncio.get_event_loop()

AGENT = web.Application(middlewares=[IndexMiddleware()])

AGENT['msg_router'] = Router()
AGENT['msg_receiver'] = Receiver()

AGENT['ui_event_queue'] = UIEventQueue(LOOP)
AGENT['ui_router'] = Router()

AGENT['agent'] = Agent()

# template engine setup
aiohttp_jinja2.setup(
    AGENT,
    loader=jinja2.FileSystemLoader(
        os.path.realpath('view/templates/')
    )
)

ROUTES = [
    web.get('/', site_handlers.index),
    web.get('/ws', AGENT['ui_event_queue'].ws_handler),
    web.post('/indy', AGENT['msg_receiver'].handle_message),
    web.post('/indy/request', connection.send_request),
    #web.get('/indy/connections', site_handlers.connections),
    web.get('/indy/accept/{did}', connection.handle_request_accepted),
    #web.get('/indy/requests', site_handlers.requests),
    web.post('/indy/init', init.initialize_agent),
    web.static('/res', 'view/res', show_index=True)
]

AGENT.add_routes(ROUTES)

RUNNER = web.AppRunner(AGENT)
LOOP.run_until_complete(RUNNER.setup())

SERVER = web.TCPSite(RUNNER, 'localhost', PORT)

async def message_process(agent):
    """ Message processing loop task.
        Message routes are also defined here through the message router.
    """
    msg_router = agent['msg_router']
    msg_receiver = agent['msg_receiver']
    ui_event_queue = agent['ui_event_queue']

    await msg_router.register("CONN_REQ", connection.handle_request_received)
    await msg_router.register("CONN_RES", connection.handle_response)

    while True:
        msg_bytes = await msg_receiver.recv()
        try:
            msg = Serializer.unpack(msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
            continue
        res = await msg_router.route(msg, agent['agent'])
        if res is not None:
            await ui_event_queue.send(json.dumps(res))

async def ui_event_process(agent):
    ui_router = agent['ui_router']
    ui_event_queue = agent['ui_event_queue']

    await ui_router.register("SEND_REQ", connection.send_request)
    await ui_router.register("UI_CONNECT", ui.ui_connect)
    await ui_router.register("AGENT_INIT", init.initialize_agent)

    while True:
        msg_bytes = await ui_event_queue.recv()
        try:
            msg = Serializer.unpack(msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
            continue
        msg = Serializer.unpack(msg_bytes)
        res = await ui_router.route(msg, agent['agent'])
        if res is not None:
            await ui_event_queue.send(json.dumps(res))

try:
    print('===== Starting Server on: http://localhost:{} ====='.format(PORT))
    LOOP.create_task(SERVER.start())
    LOOP.create_task(message_process(AGENT))
    LOOP.create_task(ui_event_process(AGENT))
    LOOP.run_forever()
except KeyboardInterrupt:
    print("exiting")
