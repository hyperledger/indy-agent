import serpy
import json

class Message(object):
    type = 'conn_req'

    def __init__(self, type, data):
        self.type = type
        self.data = data