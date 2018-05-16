import serpy
import json

class Message(object):
    def __init__(self, type, did, data):
        self.type = type
        self.did = did
        self.data = data
