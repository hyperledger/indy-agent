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

from aiohttp import web
from indy import crypto, did, error, IndyError, wallet

from modules.connection import Connection
from modules.ui import Ui
from modules.admin_walletconnection import AdminWalletConnection

import modules.ui
import serializer.json_serializer as Serializer
from receiver.message_receiver import MessageReceiver as Receiver
from router.family_router import FamilyRouter as Router
from ui_event import UIEventQueue
from model import Agent
from message_types import UI, CONN, CONN_UI, ADMIN_WALLETCONNECTION
from model import Message


AGENTINITINCLI = False
    #no cli input of walletname and passphrase
if len(sys.argv) == 2 and str.isdigit(sys.argv[1]):
    PORT = int(sys.argv[1])
    print("Option 1 -= UI")
    # args would be port agent1(name) passphrase, cont'd

elif len(sys.argv) == 4 and str.isdigit(sys.argv[1]):
    print("Option 2 - cli")
    PORT = int(sys.argv[1])
    WALLETNAME = str(sys.argv[2])
    WALLETPASS = str(sys.argv[3])
    AGENTINITINCLI = True

else:
    PORT = 8080

LOOP = asyncio.get_event_loop()

AGENT = web.Application()

aiohttp_jinja2.setup(AGENT, loader=jinja2.FileSystemLoader('view'))

AGENT['msg_router'] = Router()
AGENT['msg_receiver'] = Receiver()

AGENT['ui_event_queue'] = UIEventQueue(LOOP)
AGENT['ui_router'] = Router()

AGENT['conn_router'] = Router()
AGENT['conn_receiver'] = Receiver()

AGENT['agent'] = Agent()
AGENT['modules'] = {
    'connection': Connection(AGENT['agent']),
    'ui': Ui(AGENT['agent']),
    'admin_walletconnection': AdminWalletConnection(AGENT['agent'])
}
AGENT['agent'].modules = AGENT['modules']

UI_TOKEN = uuid.uuid4().hex
AGENT['agent'].ui_token = UI_TOKEN

ROUTES = [
    web.get('/', modules.ui.root),
    web.get('/ws', AGENT['ui_event_queue'].ws_handler),
    web.static('/res', 'view/res'),
    web.post('/indy', AGENT['msg_receiver'].handle_message),
    web.post('/offer', AGENT['conn_receiver'].handle_message)
]

AGENT.add_routes(ROUTES)

RUNNER = web.AppRunner(AGENT)
LOOP.run_until_complete(RUNNER.setup())

SERVER = web.TCPSite(runner=RUNNER, port=PORT)

async def connect_wallet(agent_name, passphrase):
    #set wallet name from msg contents

    AGENT['agent'].owner = agent_name
    wallet_name = '%s-wallet' % AGENT['agent'].owner

    wallet_config = json.dumps({"id": wallet_name})
    wallet_credentials = json.dumps({"key": passphrase})

    # pylint: disable=bare-except
    # TODO: better handle potential exceptions.
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
    except Exception as e:
        print(e)

    try:
        AGENT['agent'].wallet_handle = await wallet.open_wallet(wallet_config,
                                                       wallet_credentials)
    except Exception as e:
        print(e)
        print("Could not open wallet!")
    AGENT['agent'].initialized = True
    (_, AGENT['agent'].endpoint_vk) = await did.create_and_store_my_did(
        AGENT['agent'].wallet_handle, "{}")


if AGENTINITINCLI:
    try:
        LOOP.run_until_complete(connect_wallet(WALLETNAME, WALLETPASS))
        print("Connected to wallet via command line args:{}".format(WALLETNAME))
    except Exception as e:
        print(e)

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

    while True:
        encrypted_msg_bytes = await msg_receiver.recv()
        try:
            encrypted_msg_str = Serializer.unpack(encrypted_msg_bytes)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(encrypted_msg_bytes, e))
            continue

        encrypted_msg_bytes = base64.b64decode(encrypted_msg_str.content.encode('utf-8'))

        agent_dids_str = await did.list_my_dids_with_meta(AGENT['agent'].wallet_handle)

        agent_dids_json = json.loads(agent_dids_str)

        this_did = ""

        #  trying to find verkey for encryption
        for agent_did_data in agent_dids_json:
            try:
                decrypted_msg = await crypto.anon_decrypt(
                    AGENT['agent'].wallet_handle,
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
            "Agent doesn't have needed verkey for anon_decrypt"
            continue

        try:
            msg = Serializer.unpack(decrypted_msg)
        except Exception as e:
            print('Failed to unpack message: {}\n\nError: {}'.format(decrypted_msg, e))
            continue

        #  pass this connections did with the message
        msg.content['did'] = this_did
        msg = Serializer.unpack_dict(msg.content)

        res = await msg_router.route(msg)

        if res is not None:
            await ui_event_queue.send(Serializer.pack(res))

async def ui_event_process(agent):
    ui_router = agent['ui_router']
    ui_event_queue = agent['ui_event_queue']
    connection = agent['modules']['connection']
    ui = agent['modules']['ui']

    ui_router.register(CONN_UI.FAMILY, connection)
    ui_router.register(UI.FAMILY, ui)
    ui_router.register(ADMIN_WALLETCONNECTION.FAMILY, agent['modules']['admin_walletconnection'])

    while True:
        msg = await ui_event_queue.recv()

        if not isinstance(msg, Message):
            try:
                msg = Serializer.unpack(msg)
            except Exception as e:
                print('Failed to unpack message: {}\n\nError: {}'.format(msg, e))
                continue

        if msg.ui_token != UI_TOKEN:
            print('Invalid token received, rejecting message: {}'.format(msg))
            continue

        res = await ui_router.route(msg)
        if res is not None:
            await ui_event_queue.send(Serializer.pack(res))

try:
    print('===== Starting Server on: http://localhost:{} ====='.format(PORT))
    print('Your UI Token is: {}'.format(UI_TOKEN))
    LOOP.create_task(SERVER.start())
    LOOP.create_task(conn_process(AGENT))
    LOOP.create_task(message_process(AGENT))
    LOOP.create_task(ui_event_process(AGENT))
    LOOP.run_forever()
except KeyboardInterrupt:
    print("exiting")
