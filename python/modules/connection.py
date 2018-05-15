class Connection:

    '''
        Handles connection requests from other peers.
    '''
    def handle_request(self, data):

        pass

    '''
        decrypts anoncrypted connection response 
    '''
    def handle_response(self, data):

        pass

    '''
        sends a connection request. 
        
        a connection response contains the user's did, verkey, endpoint, and endpoint of person wanting to connect.
    '''
    def send_request(self, data):

        pass

    '''
        sends a connection response should be anon_encrypted. 
        
        a connection response will include: 
        
        - user DID, and verkey
        
    '''
    def send_response(self, data):

        pass
