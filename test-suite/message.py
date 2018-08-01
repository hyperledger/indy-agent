""" Define Message class and supporting methods.
"""

from box import Box
from typing import Dict, Any

class Message(Box):
    """ Message: the container for all information received as a message.

        Message is a "Box" type which enables the use of both dot access and
        traditional dictionary access (as in `box.thing` and `box['thing']`).

        Box also provides something called a "Frozen Box" which marks the
        elements of a Box as immutable. This means that something like

            message.type = 'something_else'

        will raise an error.

        It is also worth noting that Message objects do not necessarily have
        to be valid Indy messages.
    """
    def __init__(self, message_dictionary: Dict[str, Any]):
        """ Create a Message object using a Frozen Box.
        """
        super(Box, self).__init__(message_dictionary, frozen_box=True)

def is_valid_message(msg: Message) -> bool:
    """ Validate a Message object.
    """
    return 'type' in msg
