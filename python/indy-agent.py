""" indy-agent python implementation
"""

# Pylint struggles to find packages inside of a virtual environments;
# pylint: disable=import-error

# Pylint also dislikes the name indy-agent but this follows conventions already
# established in indy projects.
# pylint: disable=invalid-name

import asyncio
import sys
import uuid
import aiohttp_jinja2
import jinja2
import base64
import json
import argparse

from aiohttp import web
from indy import crypto, did, error, IndyError, wallet

from modules.connection import Connection
from modules.admin import Admin
from modules.admin_walletconnection import AdminWalletConnection
from modules.basicmessage import BasicMessage

import modules.admin
import serializer.json_serializer as Serializer
from receiver.message_receiver import MessageReceiver as Receiver
from router.family_router import FamilyRouter as Router
from ui_event import UIEventQueue
from message_types import ADMIN, CONN, ADMIN_CONNECTIONS, ADMIN_WALLETCONNECTION, BASICMESSAGE, ADMIN_BASICMESSAGE
from agent import Agent
from message import Message


# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("port", nargs="?", default="8080", type=int, help="The port to attach.")
parser.add_argument("--wallet", nargs=2, metavar=('walletname','walletpass'), help="The name and passphrase of the wallet to connect to.")
parser.add_argument("--ephemeralwallet", action="store_true", help="Use ephemeral wallets")
args = parser.parse_args()

# config webapp

LOOP = asyncio.get_event_loop()

WEBAPP = web.Application()

aiohttp_jinja2.setup(WEBAPP, loader=jinja2.FileSystemLoader('view'))

WEBAPP['msg_router'] = Router()
WEBAPP['msg_receiver'] = Receiver()

WEBAPP['ui_event_queue'] = UIEventQueue(LOOP)
WEBAPP['ui_router'] = Router()

WEBAPP['conn_router'] = Router()
WEBAPP['conn_receiver'] = Receiver()

WEBAPP['agent'] = Agent()
WEBAPP['modules'] = {
    'connection': Connection(WEBAPP['agent']),
    'admin': Admin(WEBAPP['agent']),
    'admin_walletconnection': AdminWalletConnection(WEBAPP['agent']),
    'basicmessage': BasicMessage(WEBAPP['agent'])
}
WEBAPP['agent'].modules = WEBAPP['modules']

UI_TOKEN = uuid.uuid4().hex
WEBAPP['agent'].ui_token = UI_TOKEN

ROUTES = [
    web.get('/', modules.admin.root),
    web.get('/ws', WEBAPP['ui_event_queue'].ws_handler),
    web.static('/res', 'view/res'),
    web.post('/indy', WEBAPP['msg_receiver'].handle_message),
    web.post('/offer', WEBAPP['conn_receiver'].handle_message)
]

WEBAPP.add_routes(ROUTES)

RUNNER = web.AppRunner(WEBAPP)
LOOP.run_until_complete(RUNNER.setup())

SERVER = web.TCPSite(runner=RUNNER, port=args.port)

if args.wallet:
    try:
        LOOP.run_until_complete(WEBAPP['agent'].connect_wallet(args.wallet[0], args.wallet[1], ephemeral=args.ephemeralwallet))
        print("Connected to wallet via command line args: {}".format(args.wallet[0]))
    except Exception as e:
        print(e)
else:
    print("Configure wallet connection via UI.")

async def conn_process(agent):
    conn_router = agent['conn_router']
    conn_receiver = agent['conn_receiver']
    ui_event_queue = agent['ui_event_queue']
    connection = agent['modules']['connection']

    conn_router.register(CONN.FAMILY, connection)

    while True:
        msg_bytes = await conn_receiver.recv()
        try:
            msg = Serializer.unpack(msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(msg_bytes, e))
            continue

        res = await conn_router.route(msg)
        if res is not None:
            await ui_event_queue.send(Serializer.pack(res))


async def message_process(agent):
    """ Message processing loop task.
        Message routes are also defined here through the message router.
    """
    msg_router = agent['msg_router']
    msg_receiver = agent['msg_receiver']
    ui_event_queue = agent['ui_event_queue']
    connection = agent['modules']['connection']

    msg_router.register(CONN.FAMILY, connection)
    msg_router.register(BASICMESSAGE.FAMILY, agent['modules']['basicmessage'])

    while True:
        encrypted_msg_bytes = await msg_receiver.recv()
        try:
            encrypted_msg_str = Serializer.unpack(encrypted_msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(encrypted_msg_bytes, e))
            continue

        encrypted_msg_bytes = base64.b64decode(encrypted_msg_str['content'].encode('utf-8'))

        agent_dids_str = await did.list_my_dids_with_meta(WEBAPP['agent'].wallet_handle)

        agent_dids_json = json.loads(agent_dids_str)

        this_did = ""

        #  trying to find verkey for encryption
        decrypted_msg = False # provide a fallthrough value if key not present.
        for agent_did_data in agent_dids_json:
            try:
                decrypted_msg = await crypto.anon_decrypt(
                    WEBAPP['agent'].wallet_handle,
                    agent_did_data['verkey'],
                    encrypted_msg_bytes
                )
                this_did = agent_did_data['did']
                #  decrypted -> found key, stop loop
                break

            except IndyError as e:
                #  key did not work
                if e.error_code == error.ErrorCode.CommonInvalidStructure:
                    print('Key did not work')
                    continue
                else:
                    #  something else happened
                    print('Could not decrypt message: {}\nError: {}'.format(
                        encrypted_msg_bytes, e))
                    continue

        if not decrypted_msg:
            print("Agent doesn't have needed verkey for anon_decrypt")
            continue

        try:
            msg = Serializer.unpack(decrypted_msg)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(decrypted_msg, e))
            continue

        #  pass this connections did with the message
        msg['content']['did'] = this_did
        msg = Serializer.unpack_dict(msg['content'])

        res = await msg_router.route(msg)

        if res is not None:
            await ui_event_queue.send(Serializer.pack(res))

async def ui_event_process(agent):
    ui_router = agent['ui_router']
    ui_event_queue = agent['ui_event_queue']
    connection = agent['modules']['connection']
    admin = agent['modules']['admin']

    ui_router.register(ADMIN_CONNECTIONS.FAMILY, connection)
    ui_router.register(ADMIN.FAMILY, admin)
    ui_router.register(ADMIN_WALLETCONNECTION.FAMILY, agent['modules']['admin_walletconnection'])
    ui_router.register(ADMIN_BASICMESSAGE.FAMILY, agent['modules']['basicmessage'])

    while True:
        msg = await ui_event_queue.recv()

        if not isinstance(msg, Message):
            try:
                msg = Serializer.unpack(msg)
            except Exception as e:
                print('Failed to unpack message: {}\n\nError: {}'.format(msg, e))
                continue

        if msg['ui_token'] != UI_TOKEN:
            print('Invalid token received, rejecting message: {}'.format(msg))
            continue

        res = await ui_router.route(msg)
        if res is not None:
            await ui_event_queue.send(Serializer.pack(res))

try:
    print('===== Starting Server on: http://localhost:{} ====='.format(args.port))
    print('Your UI Token is: {}'.format(UI_TOKEN))
    LOOP.create_task(SERVER.start())
    LOOP.create_task(conn_process(WEBAPP))
    LOOP.create_task(message_process(WEBAPP))
    LOOP.create_task(ui_event_process(WEBAPP))
    LOOP.run_forever()
except KeyboardInterrupt:
    print("exiting")
