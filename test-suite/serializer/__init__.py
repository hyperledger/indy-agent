""" Module containing serializers.

    These functions are provided as definitions of the basic interface
    that all serializers should implement.

    This abstraction is intended to allow easily switching from one form
    of serialization to another.
"""

from message import Message

def unpack(msg: bytes) -> Message: #pylint: disable=unused-argument
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
