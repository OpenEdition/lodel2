from collections import MutableMapping
from flask.sessions import SessionMixin

class LodelRamSession(MutableMapping, SessionMixin):
    
    def __init__(self, sid, *args, **kwargs):
        self.sid = sid
        self.data = dict()
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]
    
    def __iter__(self):
        return iter(self.data)
    
    def __len__(self):
        return len(self.data)
    