import json
from model.message import Message

def unpack(dump):
    msg_dict = json.loads(dump)
    return Message(msg_dict['type'], msg_dict['did'], msg_dict['data'])

def pack(msg):
    return json.dumps({"type": msg.type, "did": msg.did, "data": msg.data})
