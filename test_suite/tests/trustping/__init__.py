import uuid
from tests import validate_message
from message import Message

class TrustPing():
    FAMILY_NAME = "trust_ping"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    PING = FAMILY + "ping"
    PING_RESPONSE = FAMILY + "ping_response"

    class Ping():
        @staticmethod
        def build():
            return Message({
                '@type': TrustPing.PING,
                '@id': str(uuid.uuid4())
            })

        @staticmethod
        def validate(message):
            validate_message(
                [
                    ('@type', TrustPing.PING),
                    '@id'
                ],
                message
            )

    class Pong():
        @staticmethod
        def build(ping_id: str):
            return Message({
                '@type': TrustPing.PING_RESPONSE,
                '~thread': {'thid': ping_id }
            })

        @staticmethod
        def validate(message, ping_id):
            validate_message(
                [
                    ('@type', TrustPing.PING_RESPONSE),
                    '~thread'
                ],
                message
            )

            validate_message(
                [
                    ('thid', ping_id)
                ],
                message['~thread']
            )
