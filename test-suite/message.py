""" Define Message class and supporting methods.
"""
import json
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
        self.context = {}


    def to_dict(self):
        return self.data

    @property
    def type(self):
        return self.data["@type"]

    class MessageEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Message):
                return obj.to_dict()
            return json.JSONEncoder.default(self, obj)

    def as_json(self):
        return json.dumps(self, cls=Message.MessageEncoder)

    def pretty_print(self):
        return json.dumps(self, sort_keys=False, indent=2, cls=Message.MessageEncoder)

