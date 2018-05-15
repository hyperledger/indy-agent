from typing import Callable

class BaseRouter(object):
    async def register(msg_type: str, handler: Callable[[bytes], None]):
        """ Register a callback for messages with a given type.
        """
        raise NotImplementedError("`register` not implemented in BaseRouter!")

    async def route(msg):
        """ Route a message to it's registered callback
        """
        raise NotImplementedError("`route` not implemented in BaseRouter!")
