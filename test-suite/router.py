""" Simple router for handling Sovrin Messages.
"""
from typing import Callable, Dict, Any
from message import Message

class RouteAlreadyRegisteredException(Exception):
    """ Route Already Registered Exception.

        Raised by router.register
    """
    pass

class Router():
    """ Simple router for handling Sovrin Messages.

        Uses python dictionary to correlate a message type to a callback.
    """
    def __init__(self):
        self.routes = {}

    async def register(self, msg_type: str, handler: Callable[[bytes, Dict[str, Any]], None]):
        """ Register a callback for messages with a given type.
        """
        if msg_type in self.routes.keys():
            raise RouteAlreadyRegisteredException()

        self.routes[msg_type] = handler

    async def route(self, msg: Message, **kwargs: Any):
        """ Route a message to it's registered callback.
        """
        if msg.type in self.routes.keys():
            return await self.routes[msg.type](msg, **kwargs)
        print('No route for message, dropping')
