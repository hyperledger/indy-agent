import re
import base64

from serializer import JSONSerializer as Serializer
from message import Message
from tests import validate_message

class Connection:
    class Message:
        FAMILY_NAME = "connections"
        VERSION = "1.0"
        FAMILY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

        INVITE = FAMILY + "invitation"
        REQUEST = FAMILY + "request"
        RESPONSE = FAMILY + "response"

    class Invite:
        @staticmethod
        def parse(invite_url: str) -> Message:
            matches = re.match('(.+)?c_i=(.+)', invite_url)
            assert matches, 'Improperly formatted invite url!'

            invite_msg = Serializer.unpack(
                base64.urlsafe_b64decode(matches.group(2)).decode('utf-8')
            )

            validate_message(
                [
                    ('@type', Connection.Message.INVITE),
                    'label',
                    'recipientKeys',
                    'serviceEndpoint'
                ],
                invite_msg
            )

            return invite_msg

        @staticmethod
        def build(label: str, connection_key: str, endpoint: str) -> str:
            msg = Message({
                '@type': Connection.Message.INVITE,
                'label': label,
                'recipientKeys': [connection_key],
                'serviceEndpoint': endpoint,
                # routing_keys not specified, but here is where they would be put in the invite.
            })

            b64_invite = base64.urlsafe_b64encode(
                bytes(
                    Serializer.pack(msg),
                    'utf-8'
                )
            ).decode('ascii')

            return '{}?c_i={}'.format(endpoint, b64_invite)

    class Request:
        @staticmethod
        def parse(request: Message):
            return (
                request['connection']['DIDDoc']['publicKey'][0]['controller'],
                request['connection']['DIDDoc']['publicKey'][0]['publicKeyBase58'],
                request['connection']['DIDDoc']['service'][0]['serviceEndpoint']
            )

        @staticmethod
        def build(label: str, my_did: str, my_vk: str, endpoint: str) -> Message:
            return Message({
                '@type': Connection.Message.REQUEST,
                'label': label,
                'connection': {
                    'DID': my_did,
                    'DIDDoc': {
                        "@context": "https://w3id.org/did/v1",
                        "publicKey": [{
                            "id": my_did + "#keys-1",
                            "type": "Ed25519VerificationKey2018",
                            "controller": my_did,
                            "publicKeyBase58": my_vk
                        }],
                        "service": [{
                            "type": "IndyAgent",
                            "recipientKeys": [my_vk],
                            #"routingKeys": ["<example-agency-verkey>"],
                            "serviceEndpoint": endpoint,
                        }],
                    }
                }
            })

        @staticmethod
        def validate(request):
            validate_message(
                [
                    ('@type', Connection.Message.REQUEST),
                    'label',
                    'connection'
                ],
                request
            )

            validate_message(
                [
                    'DID',
                    'DIDDoc'
                ],
                request['connection']
            )

            Connection.DIDDoc.validate(request['connection']['DIDDoc'])

    class Response:
        @staticmethod
        def build(my_did: str, my_vk: str, endpoint: str) -> Message:
            return Message({
                '@type': Connection.Message.RESPONSE,
                'connection': {
                    'DID': my_did,
                    'DIDDoc': {
                        "@context": "https://w3id.org/did/v1",
                        "publicKey": [{
                            "id": my_did + "#keys-1",
                            "type": "Ed25519VerificationKey2018",
                            "controller": my_did,
                            "publicKeyBase58": my_vk
                        }],
                        "service": [{
                            "type": "IndyAgent",
                            "recipientKeys": [my_vk],
                            #"routingKeys": ["<example-agency-verkey>"],
                            "serviceEndpoint": endpoint,
                        }],
                    }
                }
            })

        @staticmethod
        def validate_pre_sig(response: Message):
            validate_message(
                [
                    ('@type', Connection.Message.RESPONSE),
                    'connection~sig'
                ],
                response
            )

        @staticmethod
        def validate(response: Message):
            validate_message(
                [
                    ('@type', Connection.Message.RESPONSE),
                    'connection'
                ],
                response
            )

            validate_message(
                [
                    'DID',
                    'DIDDoc'
                ],
                response['connection']
            )

            Connection.DIDDoc.validate(response['connection']['DIDDoc'])

    class DIDDoc:
        @staticmethod
        def validate(diddoc):
            validate_message(
                [
                    '@context',
                    'publicKey',
                    'service'
                ],
                diddoc
            )

            for publicKeyBlock in diddoc['publicKey']:
                validate_message(
                    [
                        'id',
                        'type',
                        'controller',
                        'publicKeyBase58'
                    ],
                    publicKeyBlock
                )

            for serviceBlock in diddoc['service']:
                validate_message(
                    [
                        ('type', 'IndyAgent'),
                        'recipientKeys',
                        'serviceEndpoint'
                    ],
                    serviceBlock
                )
