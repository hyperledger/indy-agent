import serpy
import json

class Message(object):
    def __init__(self, type, data):
        self.type = type
        self.data = data