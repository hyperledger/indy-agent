""" Serializer using json as i/o format.
"""

import json
from model import Message

def unpack(dump: bytes) -> Message:
    """ Deserialize from json string to Message.
    """
    msg_dict = json.loads(dump)
    return Message(msg_dict['type'], msg_dict['did'], msg_dict['data'])

def pack(msg: Message) -> bytes:
    """ Serialize from Message to json string.
    """
    return json.dumps({"type": msg.msg_type, "did": msg.did, "data": msg.data})
