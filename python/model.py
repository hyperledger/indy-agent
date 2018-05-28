""" Data Model Classes.
"""

# Generally, in Python, classes are not intended to be used for data alone.
# These types of classes usually fit better as a dictionary. Here, however,
# we use classes to formalize the data being stored in these objects.

# pylint: disable=too-few-public-methods

class Agent:
    """ Data Model for all information needed for agent operation.
    """
    def __init__(self):
        self.owner = None
        self.wallet_handle = None
        self.endpoint = None
        self.pool_handle = None
        self.received_requests = {}
        self.connections = {}
        self.initialized = False

class Message(object):
    """ Data Model for messages.
    """
    def __init__(self, msg_type, did, data):
        self.msg_type = msg_type
        self.did = did
        self.data = data
