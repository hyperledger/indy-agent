""" Module containing serializers.

    These functions are provided as definitions of the basic interface
    that all serializers should implement.

    This abstraction is intended to allow easily switching from one form
    of serialization to another.
"""

import json
from message import Message

class BaseSerializer(object):
    def unpack(dump: bytes) -> Message: #pylint: disable=unused-argument
        """ Deserialize to Message.
        """

        raise NotImplementedError("Unpack method in serialzer module \
            is not implemented. Use the methods contained in a submodule of \
            serializer, such as json_serializer.")

    def pack(msg: Message) -> bytes: #pylint: disable=unused-argument
        """ Serialize to bytes.
        """

        raise NotImplementedError("Pack method in serialzer module \
            is not implemented. Use the methods contained in a submodule of \
            serializer, such as json_serializer.")

class JSONSerializer(BaseSerializer):
    """ Serializer using json as i/o format.
    """
    def unpack(dump: bytes):
        """ Deserialize from json string to Message, if it looks like a Message.
            Returns a dictionary otherwise.
        """
        def as_message(dct):
            return Message(dct)

        return json.loads(dump, object_hook=as_message)

    def pack(msg: Message) -> bytes:
        """ Serialize from Message to json string or from dictionary to json string.
        """
        return json.dumps(msg.to_dict())
