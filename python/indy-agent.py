""" indy-agent python implementation
"""

# Pylint struggles to find packages inside of a virtual environments;
# pylint: disable=import-error

# Pylint also dislikes the name indy-agent but this follows conventions already
# established in indy projects.
# pylint: disable=invalid-name

import argparse
import asyncio
import jinja2
import aiohttp_jinja2
from aiohttp import web

from modules.connection import Connection, AdminConnection
from modules.admin import Admin, root
from modules.admin_walletconnection import AdminWalletConnection
from modules.basicmessage import AdminBasicMessage, BasicMessage
from modules.trustping import AdminTrustPing, TrustPing
from post_message_handler import PostMessageHandler
from websocket_message_handler import WebSocketMessageHandler
from agent import Agent
from message import Message

if __name__ == "__main__":

    # Argument Parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", default="8080", type=int, help="The port to attach.")
    parser.add_argument(
        "--wallet",
        nargs=2,
        metavar=('walletname', 'walletpass'),
        help="The name and passphrase of the wallet to connect to."
    )
    parser.add_argument("--ephemeralwallet", action="store_true", help="Use ephemeral wallets")
    args = parser.parse_args()

    # Configure webapp
    LOOP = asyncio.get_event_loop()
    WEBAPP = web.Application()
    aiohttp_jinja2.setup(WEBAPP, loader=jinja2.FileSystemLoader('view'))

    AGENT = Agent()
    POST_MESSAGE_HANDLER = PostMessageHandler(AGENT.message_queue)
    WEBSOCKET_MESSAGE_HANDLER = WebSocketMessageHandler(
        AGENT.message_queue,
        AGENT.outbound_admin_message_queue
    )

    ROUTES = [
        web.get('/', root),
        web.get('/ws', WEBSOCKET_MESSAGE_HANDLER.ws_handler),
        web.static('/res', 'view/res'),
        web.post('/indy', POST_MESSAGE_HANDLER.handle_message),
    ]

    WEBAPP['agent'] = AGENT
    WEBAPP.add_routes(ROUTES)

    RUNNER = web.AppRunner(WEBAPP)
    LOOP.run_until_complete(RUNNER.setup())

    SERVER = web.TCPSite(runner=RUNNER, port=args.port)

    # Agent Module Registration
    AGENT.register_module(Admin)
    AGENT.register_module(Connection)
    AGENT.register_module(AdminConnection)
    AGENT.register_module(AdminWalletConnection)
    AGENT.register_module(BasicMessage)
    AGENT.register_module(AdminBasicMessage)
    AGENT.register_module(AdminTrustPing)
    AGENT.register_module(TrustPing)

    if args.wallet:
        try:
            LOOP.run_until_complete(
                AGENT.connect_wallet(
                    args.wallet[0],
                    args.wallet[1],
                    ephemeral=args.ephemeralwallet
                )
            )
            print("Connected to wallet via command line args: {}".format(args.wallet[0]))
        except Exception as e:
            print(e)
    else:
        print("Configure wallet connection via UI.")

    # Main loop
    try:
        print('===== Starting Server on: http://localhost:{} ====='.format(args.port))
        LOOP.create_task(SERVER.start())
        LOOP.create_task(AGENT.start())
        LOOP.run_forever()
    except KeyboardInterrupt:
        print("exiting")
