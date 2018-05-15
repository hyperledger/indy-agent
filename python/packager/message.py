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
        return MessageSerializer(self).data

class MessageSerializer(serpy.Serializer):
    type = serpy.StrField()
    data = serpy.Field()
