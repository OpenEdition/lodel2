from collections import MutableMapping
from flask.sessions import SessionMixin
import os
from pickle import loads, dumps, UnpicklingError


class LodelFileSystemSession(MutableMapping, SessionMixin):
    
    def __init__(self, directory, sid, *args, **kwargs):
        self.path = os.path.join(directory, sid)
        self.sid = sid
        self.read()
    
    def __getitem__(self, key):
        self.read()
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()
    
    def __delitem__(self, key):
        del self.data[key]
        self.save()
    
    def __iter__(self):
        return iter(self.data)
    
    def __len__(self):
        return len(self.data)
    
    ## @brief Loads a session from a file
    # @todo Specify dedicated behaviour for each exception case
    def read(self):
        try:
            with open(self.path, 'rb') as session_file:
                self.data = loads(session_file.read())
        except FileNotFoundError:
            self.data = {}
        except (ValueError, EOFError, UnpicklingError):
            self.data = {}
    
    ## @brief Dumps a session to a file
    def save(self):
        new_name = '{}.new'.format(self.path)
        with open(new_name, 'wb') as session_file:
            session_file.write(dumps(self.data))
        os.rename(new_name, self.path)