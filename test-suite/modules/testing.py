from typing import Dict, Any
from message import Message
from router import Router
from serializer import JSONSerializer as Serializer

class MESSAGE_TYPES:
    SEND_MESSAGE = 'urn:ssi:message:sovrin.org/testing/1.0/send_message_command'

# TODO: Add some way of validating the sender
class SendMessageCommand(Message):
    def __init__(self, to: str, content: Dict[str, Any]):
        self.type = MESSAGE_TYPES.SEND_MESSAGE
        self.to = to
        self.content = content

    def valid(msg: Message):
        return msg.type == MESSAGE_TYPES.SEND_MESSAGE

    def from_message(msg: Message):
        return SendMessageCommand(msg.vars['to'], msg.vars['content'])

    def flatten(self):
        if isinstance(self.content, Message):
            content = self.content.flatten()
        else:
            content = self.content
        return {'type': self.type, 'to': self.to, 'content': content}

# -- Handlers --
async def handle_send_message(msg: Message, **kwargs):
    print('handling send message')
    transport = kwargs['transport']
    send_cmd = SendMessageCommand.from_message(msg)
    if isinstance(send_cmd.content, Message):
        await transport.send(send_cmd.to, Serializer.pack(send_cmd.content))
        return
    print('Invalid send cmd message')

# -- Routes --
async def register_routes(router: Router):
    await router.register(MESSAGE_TYPES.SEND_MESSAGE, handle_send_message)
