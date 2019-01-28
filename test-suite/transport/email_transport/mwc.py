import re

import mtc

def _make_json_key_value_pat(key):
    pat_txt = r'"%s"\s*:\s*"([^"]+)"' % key
    return re.compile(pat_txt, re.S)

_id_pat = _make_json_key_value_pat('@id')
_type_pat = _make_json_key_value_pat('@type')
_squeeze_pat = re.compile('\\s*\n[\t ]*')

class MessageWithContext:
    '''
    Hold a message plus its associated trust context, sender, and other metadata.
    '''
    def __init__(self, msg:str=None, sender:str=None, tc:mtc.MessageTrustContext=None):
        # Enforce precondition on datatype of sender
        if sender:
            assert isinstance(sender, str)
        self.msg = msg
        self.sender = sender
        self.in_reply_to = None
        self.subject = None
        if tc is None:
            tc = mtc.MessageTrustContext()
        # If we have a DID or key as the sender, then we know who sent it with confidence.
        # TODO: we need to split sender and reply email address apart. They're different
        # concepts. What we're calling sender here is authenticated_origin. All messages
        # should have a reply address.
        if sender and ('@' not in sender):
            tc.authenticated_origin = True
        self.tc = tc
        self.obj = None
    def __bool__(self):
        return bool(self.msg)
    def __str__(self):
        msg_fragment = None
        if self.msg:
            m = _id_pat.search(self.msg)
            if m:
                msg_fragment = '{..."@id":"%s"...}' % m.group(1)
            else:
                if len(self.msg) <= 40:
                    msg_fragment = _squeeze_pat.sub(' ', self.msg)
                else:
                    msg_fragment = self.msg[:60].strip().replace('\r','')
                    msg_fragment = _squeeze_pat.sub(' ', msg_fragment)
                    msg_fragment = msg_fragment[:37] + '...'
        else:
            msg_fragment = '(empty)'
        sender = self.sender
        if not sender:
            sender = 'nobody'
        return '%s from %s with %s' % (msg_fragment, sender, str(self.tc))
    def get_type(self):
        if self.msg:
            match = _type_pat.search(self.msg)
            if match:
                return match.group(1)

'''A special global constant representing degenerate, empty MessageWithContext.'''
NULL_MWC = MessageWithContext()
