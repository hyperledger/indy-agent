'''
    Handles connection requests from other peers.
'''
def handle_request(data, wallet_handle):
    print("Connection request received")
    print(data)
    print(wallet_handle)

'''
    decrypts anoncrypted connection response
'''
def handle_response(data, wallet_handle):

    pass

'''
    sends a connection request.

    a connection response contains the user's did, verkey, endpoint, and endpoint of person wanting to connect.
'''
def send_request(data, wallet_handle):

    pass

'''
    sends a connection response should be anon_encrypted.

    a connection response will include:

    - user DID, and verkey

'''
def send_response(data, wallet_handle):

    pass
