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
import uuid
from aiohttp import web

from receiver.message_receiver import MessageReceiver as Receiver
from router.simple_router import SimpleRouter as Router
from ui_event import UIEventQueue
from model import Agent
from message_types import CONN, UI
import modules.connection as connection
import modules.init as init
import modules.ui as ui
import serializer.json_serializer as Serializer

if len(sys.argv) == 2 and str.isdigit(sys.argv[1]):
    PORT = int(sys.argv[1])
else:
    PORT = 8080

LOOP = asyncio.get_event_loop()

AGENT = web.Application()

AGENT['msg_router'] = Router()
AGENT['msg_receiver'] = Receiver()

AGENT['ui_event_queue'] = UIEventQueue(LOOP)
AGENT['ui_router'] = Router()

AGENT['agent'] = Agent()
UI_TOKEN = uuid.uuid4().hex
AGENT['agent'].ui_token = UI_TOKEN

ROUTES = [
    web.get('/', ui.root),
    web.get('/ws', AGENT['ui_event_queue'].ws_handler),
    web.static('/res', 'view/res'),
    web.post('/indy', AGENT['msg_receiver'].handle_message),
    web.post('/offer', connection.offer_recv)
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

    await msg_router.register(CONN.REQUEST, connection.handle_request)
    await msg_router.register(CONN.RESPONSE, connection.handle_response)

    while True:
        encrypted_msg_bytes = await msg_receiver.recv()

        try:
            decrypted_msg_bytes = await crypto.anon_decrypt(
                    agent.wallet_handle,
                    agent.endpoint_vk,
                    encrypted_msg_bytes
                    )
        except Exception as e:
            print('Could not decrypt message: {}\nError: {}'.format(encrypted_msg_bytes, e))
            continue

        try:
            msg = Serializer.unpack(msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
            continue

        res = await msg_router.route(msg, agent['agent'])
        if res is not None:
            await ui_event_queue.send(Serializer.pack(res))

async def ui_event_process(agent):
    ui_router = agent['ui_router']
    ui_event_queue = agent['ui_event_queue']

    await ui_router.register(UI.SEND_OFFER, connection.send_offer)
    await ui_router.register(UI.STATE_REQUEST, ui.ui_connect)
    await ui_router.register(UI.INITIALIZE, init.initialize_agent)

    while True:
        msg_bytes = await ui_event_queue.recv()
        try:
            msg = Serializer.unpack(msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
            continue

        if msg.id != UI_TOKEN:
            print('Invalid token received, rejecting message: {}'.format(msg_bytes))
            continue

        res = await ui_router.route(msg, agent['agent'])
        if res is not None:
            await ui_event_queue.send(Serializer.pack(res))

try:
    print('===== Starting Server on: http://localhost:{} ====='.format(PORT))
    print('Your UI Token is: {}'.format(UI_TOKEN))
    LOOP.create_task(SERVER.start())
    LOOP.create_task(message_process(AGENT))
    LOOP.create_task(ui_event_process(AGENT))
    LOOP.run_forever()
except KeyboardInterrupt:
    print("exiting")
