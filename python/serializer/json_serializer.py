import json
from model import Message

def unpack(dump):
    msg_dict = json.loads(dump)
    return Message(msg_dict['type'], msg_dict['did'], msg_dict['data'])

def pack(msg):
    return json.dumps({"type": msg.msg_type, "did": msg.did, "data": msg.data})
