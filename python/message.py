""" Module defining the Message class that is used as base structure for all
    received messages.
"""
from collections import UserDict


class Message(UserDict):
    """ Data Model for messages.
    """
    def __init__(self, *args, **kwargs):
        """ Create a Message object

        @type: string denoting the message type. Standardization efforts are in progress.
        @id: identifier for message. Usually a nonce or a DID. This combined with the type
            tell us how to interpret the message.
        other things: ambiguous data. Interpretation defined by type and id.

        """
        UserDict.__init__(self,*args, **kwargs)


    def to_dict(self):
        return self.data

    @property
    def type(self):
        return self.data["@type"]
