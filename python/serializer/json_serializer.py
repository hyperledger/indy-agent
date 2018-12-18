"""
Serializer using json as i/o format.
"""

import json

from message import Message


def unpack_dict(dictionary: dict) -> Message:
    deserialized_msg = Message(dictionary)
    return deserialized_msg


def unpack(dump) -> Message:
    """
    Deserialize from bytes or str to Message
    """
    dump_dict = json.loads(dump)
    deserialized_msg = Message(dump_dict)
    return deserialized_msg


def pack(msg: Message) -> str:
    """
    Serialize from Message to json string or from dictionary to json string.
    """

    class MessageEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Message):
                return obj.to_dict()
            return json.JSONEncoder.default(self, obj)

    return json.dumps(msg, cls=MessageEncoder)
