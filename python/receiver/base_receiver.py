""" Base class for receivers. """

class BaseReceiver(object):
    """ Base class for receivers used to implement different methods of receiving messages. """

    def start():
        """ Setup and start receiver.
        """
        raise NotImplementedError("`start` not implemented in BaseReceiver")

    #async def recv():
    #    """ Asynchronously receive message.
    #        
    #        :return bytes
    #    """
    #    raise NotImplementedError("`recv` not implemented in BaseReceiver")
