import pytest
import json

from message import Message
from tests import pack

@pytest.mark.asyncio
async def test_got_ttt_res(emailTransport):
    msg_send = Message({
        '@type': "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/tictactoe/1.0/move",
        "@id": "518be002-de8e-456e-b3d5-8fe472477a86",
              "ill_be": "X",
              "moves": ["X:B2"],
              "comment_ltxt": "Let's play tic-tac-to. I'll be X. I pick cell B2."
    })

    securemsg = emailTransport.securemsg

    msg = await pack(securemsg.wallet_handle, securemsg.my_vk, securemsg.their_vk, msg_send)

    received_msg = emailTransport.send_encrypted_store_resp(msg)

    received_msg = json.loads(received_msg.decode("utf-8"))
    assert received_msg["@type"] == 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/tictactoe/1.0/move'
