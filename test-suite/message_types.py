""" Message Type Definitions, organized by class
"""

class CONN:
    """ Connetion Class of Message Types.

        This type notation is still being discussed and may change.
    """
    OFFER = "urn:sovrin:agent:message_type:sovrin.org/connection_offer"
    REQUEST = "urn:sovrin:agent:message_type:sovrin.org/connection_request"
    RESPONSE = "urn:sovrin:agent:message_type:sovrin.org/connection_response"
    ACKNOWLEDGE = "urn:sovrin:agent:message_type:sovrin.org/connection_acknowledge"

class UI:
    STATE = "urn:sovrin:agent:message_type:sovrin.org/ui/state"
    STATE_REQUEST = "urn:sovrin:agent:message_type:sovrin.org/ui/state_request"
    SEND_OFFER = "urn:sovrin:agent:message_type:sovrin.org/ui/send_offer"
    INITIALIZE = "urn:sovrin:agent:message_type:sovrin.org/ui/initialize"
    OFFER_RECEIVED = "urn:sovrin:agent:message_type:sovrin.org/ui/offer_received"
    OFFER_SENT = "urn:sovrin:agent:message_type:sovrin.org/ui/offer_sent"
