""" Serializer using json as i/o format.
"""

import json
from model import Message

def unpack(dump: bytes):
    """ Deserialize from json string to Message, if it looks like a Message.
        Returns a dictionary otherwise.
    """
    def as_message(dct):
        if 'type' in dct and 'id' in dct and 'message' in dct:
                return Message(dct['type'], dct['id'], dct['message'])

        return dct

    return json.loads(dump, object_hook=as_message)

def pack(obj) -> bytes:
    """ Serialize from Message to json string or from dictionary to json string.
    """
    class MessageEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Message):
                return {'type': obj.type, 'id': obj.id, 'message': obj.message}
            return json.JSONEncoder.default(self, obj)

    return json.dumps(obj, cls=MessageEncoder)
