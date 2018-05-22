class Agent:
    def __init__(self):
        self.me = None
        self.wallet_handle = None
        self.endpoint = None
        self.pool_handle = None
        self.received_requests = {}
        self.connections = {}
        self.initialized = False

