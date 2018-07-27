from typing import Dict, Any

class Message(object):
    def __init__(self, message_dictionary: Dict[str, Any]):
        self.type = message_dictionary['type']
        del message_dictionary['type']
        self.vars = message_dictionary

    def flatten(self):
        return {'type': self.type, **self.vars}

    def valid(message_dictionary: Dict[str, Any]) -> bool:
        if isinstance(message_dictionary, Message):
            return True
        return 'type' in message_dictionary.keys()
