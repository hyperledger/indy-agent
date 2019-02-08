import asyncio
import pytest
import json
from indy import crypto, did, wallet

from message import Message
from modules.testing import MESSAGE_TYPES as TESTING_MESSAGE
from serializer import JSONSerializer as Serializer
from tests import expect_message,validate_message
from tests import pack

@pytest.mark.asyncio
async def test_got_ttt_res(emailTransport):
    msg = Message({
        '@type': "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/tictactoe/1.0/move",
        "@id": "518be002-de8e-456e-b3d5-8fe472477a86",
              "ill_be": "X",
              "moves": ["X:B2"],
              "comment_ltxt": "Let's play tic-tac-to. I'll be X. I pick cell B2."
    })
    # msg = {
    #           "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/tictactoe/1.0/move",
    #           "@id": "518be002-de8e-456e-b3d5-8fe472477a86",
    #           "ill_be": "X",
    #           "moves": ["X:B2"],
    #           "comment_ltxt": "Let's play tic-tac-to. I'll be X. I pick cell B2."
    #       }
    securemsg = emailTransport.securemsg
    # msg_str = json.dumps(msg)
    #
    # with open('plaintext.txt', 'w') as f:
    #     f.write(msg_str)
    # with open('plaintext.txt', 'rb') as f:
    #     msg_bytes = f.read()

    msg = await pack(securemsg.wallet_handle, securemsg.my_vk, securemsg.their_vk, msg)
    received_msg = emailTransport.send_encrypted_store_resp(msg)

    received_msg = json.loads(received_msg.decode("utf-8"))
    assert received_msg["@type"] == 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/tictactoe/1.0/move'
