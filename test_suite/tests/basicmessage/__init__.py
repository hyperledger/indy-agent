import datetime
from message import Message
from tests import expect_message, validate_message, pack, unpack, sign_field, unpack_and_verify_signed_field

class BasicMessage():
    FAMILY_NAME = "basicmessage"
    VERSION = "1.0"
    FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    MESSAGE = FAMILY + "message"

    @staticmethod
    def build(content: str) -> Message:
        sent_time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(' ')
        return Message({
            '@type': BasicMessage.MESSAGE,
            '~l10n': {'locale': 'en'},
            'sent_time': sent_time,
            'content': content
        })

    def validate(msg: Message):
        validate_message(
            [
                ('@type', BasicMessage.MESSAGE),
                '~l10n',
                'sent_time',
                'content',
            ],
            msg
        )

        validate_message(
            [
                ('locale', 'en')
            ],
            msg['~l10n']
        )
