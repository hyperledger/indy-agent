class BaseCryptor(object):
    """ Base class for encryption and decryption operations
    """

    def auth_crypt(self, msg: bytes, recipient_vk: str, sender_vk: str):
        """ Encrypt message for receiver with verifiable sender

            :param msg - bytes

            :return encrypted byte string
        """
        raise NotImplementedError("auth_crypt not implemented for BaseCryptor!")

    def auth_decrypt(self, msg: bytes, recipient_vk: str):
        """ Decrypt message for receiver with verifiable sender
            
            :param msg - encrypted bytes
            : return 
        """
        raise NotImplementedError("auth_decrypt not implemented for BaseCryptor!")

    def anon_crypt(self, msg: bytes, recipient_vk: str, sender_vk: str):
        """ Encrypt message for receiver with verifiable sender

            :param msg - bytes

            :return encrypted byte string
        """
        raise NotImplementedError("auth_crypt not implemented for BaseCryptor!")

    def anon_decrypt(self, msg: bytes, recipient_vk: str):
        """ Decrypt message for receiver with verifiable sender
            
            :param msg - encrypted bytes
            : return 
        """
        raise NotImplementedError("auth_decrypt not implemented for BaseCryptor!")
