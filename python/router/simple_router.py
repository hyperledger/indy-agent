from typing import Callable
from .base_router import BaseRouter
from serializer.message import Message

class SimpleRouter(BaseRouter):
    def __init__(self):
        self.routes = {}

    async def register(self, msg_type: str, handler: Callable[[bytes], None]):
        """ Register a callback for messages with a given type.
        """
        if msg_type in self.routes.keys():
            raise router.RouteAlreadyRegisteredException()

        self.routes[msg_type] = handler

    async def route(self, msg, wallet_handle):
        """ Route a message to it's registered callback
        """
        if msg.type in self.routes.keys():
            await self.routes[msg.type](msg.data, wallet_handle)
