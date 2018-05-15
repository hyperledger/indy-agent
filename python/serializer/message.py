import serpy
import json

class Message(object):
    type = 'conn_req'

    def __init__(self, type, data):
        self.type = type
        self.data = data

    def from_json(dump):
        msg = json.loads(dump)
        type = msg["type"]
        data = msg["data"]
        return Message(type, data)

    def to_json(self):
        msg_dict = {"type": self.type, "data": self.data}
        return json.dumps(msg_dict)
        #return MessageSerializer(self).data

class MessageSerializer(serpy.Serializer):
    type = serpy.StrField()
    data = serpy.Field()
