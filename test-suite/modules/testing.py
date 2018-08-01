""" An example message family definition.
"""

from typing import Dict, Any
from message import Message
from router import Router
from serializer import JSONSerializer as Serializer

class MESSAGE_TYPES:
    SEND_MESSAGE = 'urn:ssi:message:sovrin.org/testing/1.0/send_message_command'

def is_valid_send_message(msg: Message):
    """ Validate that a given message has the correct structure for a "send_message_command."
    """
    expected_attributes = [
        'type',
        'to',
        'content'
    ]

    for attribute in expected_attributes:
        if attribute not in msg:
            return False

    return True

# -- Handlers --
# These handlers are used exclusively in the included agent,
# not the test-suite.
async def handle_send_message(msg: Message, **kwargs):
    """ Message handler for send_message_command.
    """
    transport = kwargs['transport']
    if is_valid_send_message(msg):
        await transport.send(msg.to, Serializer.pack(msg.content))
        return
    print('invalid send message command dropped')

# -- Routes --
# These routes are used exclusivel in the included agent, not the test-suite.
async def register_routes(router: Router):
    """ Route registration for send_message_command.
    """
    await router.register(MESSAGE_TYPES.SEND_MESSAGE, handle_send_message)
