<<<<<<< HEAD
import asyncio
import time
import re
from indy import crypto, did, wallet


=======
>>>>>>> 06e09cf26898c92ae1cc5599e171089cdc360d21
'''
    Handles connection requests from other peers.
'''
def handle_request(data, wallet_handle):
<<<<<<< HEAD

    pass

'''
    decrypts anoncrypted connection response 
'''
def handle_response(self, data, wallet_handle):

    decrypted = await crypto.auth_decrypt(wallet_handle, my_vk, data)
    msg = decrypted.__getitem__(1).decode()
    print(msg)
=======
    print("Connection request received")
    print(data)
    print(wallet_handle)

'''
    decrypts anoncrypted connection response
'''
def handle_response(data, wallet_handle):
>>>>>>> 06e09cf26898c92ae1cc5599e171089cdc360d21

    pass

'''
<<<<<<< HEAD
    sends a connection request. 
    
=======
    sends a connection request.

>>>>>>> 06e09cf26898c92ae1cc5599e171089cdc360d21
    a connection response contains the user's did, verkey, endpoint, and endpoint of person wanting to connect.
'''
def send_request(data, wallet_handle):

    pass

'''
<<<<<<< HEAD
    sends a connection response should be anon_encrypted. 
    
    a connection response will include: 
    
    - user DID, and verkey
    
=======
    sends a connection response should be anon_encrypted.

    a connection response will include:

    - user DID, and verkey

>>>>>>> 06e09cf26898c92ae1cc5599e171089cdc360d21
'''
def send_response(data, wallet_handle):

    pass
