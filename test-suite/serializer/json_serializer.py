""" Serializer using json as i/o format.
"""

import json
from message import Message

def unpack(dump: bytes):
    """ Deserialize from json string to Message, if it looks like a Message.
        Returns a dictionary otherwise.
    """
    def as_message(dct):
        if Message.valid(dct):
            return Message(dct)

        return dct

    return json.loads(dump, object_hook=as_message)

def pack(msg: Message) -> bytes:
    """ Serialize from Message to json string or from dictionary to json string.
    """
    return json.dumps(msg.flatten())
