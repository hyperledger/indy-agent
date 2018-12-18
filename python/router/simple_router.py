""" Simple router for handling Sovrin Messages.
"""

from typing import Callable
from agent import Agent
from message import Message
from . import BaseRouter, RouteAlreadyRegisteredException

class SimpleRouter(BaseRouter):
    """ Simple router for handling Sovrin Messages.

        Uses python dictionary to correlate a message type to a callback.
    """
    def __init__(self):
        self.routes = {}

    def register(self, msg_type: str, handler: Callable[[Message], None]):
        """ Register a callback for messages with a given type.
        """
        if msg_type in self.routes.keys():
            raise RouteAlreadyRegisteredException()

        self.routes[msg_type] = handler

    async def route(self, msg: Message):
        """ Route a message to it's registered callback.
        """
        if msg.type in self.routes.keys():
            return await self.routes[msg.type](msg)
