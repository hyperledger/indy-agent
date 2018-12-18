""" Message Type Definitions, organized by class
"""


class ADMIN:
    FAMILY = "admin"
    VERSION = "1.0"
    BASE = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY + "/" + VERSION + "/"

    STATE = BASE + "state"
    STATE_REQUEST = BASE + "state_request"

class ADMIN_CONNECTIONS:
    FAMILY = "admin_connections"
    VERSION = "1.0"
    BASE = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY + "/" + VERSION + "/"

    CONNECTION_LIST = BASE + "connection_list"
    CONNECTION_LIST_REQUEST = BASE + "connection_list_request"

    SEND_INVITE = BASE + "send_invite"
    INVITE_SENT = BASE + "invite_sent"
    INVITE_RECEIVED = BASE + "invite_received"

    REQUEST_RECEIVED = BASE + "request_received"
    RESPONSE_RECEIVED = BASE + "response_received"

    SEND_REQUEST = BASE + "send_request"
    REQUEST_SENT = BASE + "request_sent"

    SEND_RESPONSE = BASE + "send_response"
    RESPONSE_SENT = BASE + "response_sent"

class BASICMESSAGE:
    FAMILY = "basicmessage"
    VERSION = "1.0"
    BASE = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY + "/" + VERSION + "/"

    MESSAGE = BASE + "message"

class ADMIN_BASICMESSAGE:
    FAMILY = "admin_basicmessage"
    VERSION = "1.0"
    BASE = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY + "/" + VERSION + "/"

    MESSAGE_RECEIVED = BASE + "message_received"
    SEND_MESSAGE = BASE + "send_message"
    MESSAGE_SENT = BASE + "message_sent"

class ADMIN_WALLETCONNECTION:
    FAMILY = "admin_walletconnection"
    VERSION = "1.0"
    BASE = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY + "/" + VERSION + "/"

    CONNECT = BASE + "connect"
    DISCONNECT = BASE + "disconnect"
    USER_ERROR = BASE + "user_error"

class CONN:
    FAMILY = "connections"
    VERSION = "1.0"
    BASE = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY + "/" + VERSION + "/"

    INVITE = BASE + "invite"
    REQUEST = BASE + "request"
    RESPONSE = BASE + "response"

class FORWARD:
    BASE = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/"

    FORWARD_TO_KEY = BASE + "forward_to_key"
    FORWARD = BASE + "forward"
