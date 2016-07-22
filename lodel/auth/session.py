# -*- coding; utf-8 -*-

from abc import ABC, abstractmethod
from uuid import uuid1

from werkzeug.contrib.sessions import generate_key, Session

from lodel.auth.exceptions import AuthenticationError
from lodel.utils.datetime import get_utc_timestamp


class LodelSession(ABC):
    expiration_limit = 900

    __sessions = {}

    ## @brief creates a session
    # @param contests dict : session initialization keys
    def __init__(self, contents={}):

        self.sid = self.__class__.generate_new_sid()

        for key, value in contents.items():
            self.set_key(key, value)

        self.store()
        self.register_session()

    ## @brief stores the session
    @abstractmethod
    def store(self):
        pass

    ## @brief registers the session
    @abstractmethod
    def register_session(self):
        pass

    ## @brief saves a session
    @abstractmethod
    def save(self):
        pass

    ## @brief loads a session
    # @param sid str : session id
    # @return LodelSession
    @classmethod
    @abstractmethod
    def load(cls, sid):
        return None

    ## @brief cleans the session store
    @classmethod
    @abstractmethod
    def clean(cls):
        pass

    ## @brief destroys a session
    # @param sid str : session id
    @classmethod
    def destroy(cls, sid):
        cls.delete_session(sid)
        cls.unregister_session(sid)

    ## @brief deletes a session
    # @param sid str : session id
    @classmethod
    @abstractmethod
    def delete_session(cls, sid):
        pass

    ## @brief unregisters a session from the session store list
    # @param sid str : session id
    @classmethod
    def unregister_session(cls, sid):
        if sid in cls.__sessions:
            del cls.__sessions[sid]

    ## @brief checks if a session if registered
    # @param sid str : session id
    # @return bool
    @classmethod
    def is_registered(cls, sid):
        return (sid in cls.__sessions)


    ## @brief checks if a session is expired
    # @param sid str : session id
    @classmethod
    def is_expired(cls, sid):
        expiration_timestamp = cls.get_last_modified(sid) + cls.EXPIRATION_LIMIT
        now_timestamp = get_utc_timestamp()
        return now_timestamp > expiration_timestamp

    ## @brief gets the timestamp of the last modification
    # @param sid str : session id
    # @return float
    @classmethod
    @abstractmethod
    def get_last_modified(cls, sid):
        return 0.0

    ## @brief generates a new session id
    # @return sid
    # @todo find a more secure way of building a session id
    @classmethod
    def generate_new_sid(cls):
        return uuid1()

    ## @brief sets a key's value in the session
    # @param key str
    # @param value unknown
    def set_key(self, key, value):
        setattr(self, key, value)
        self.save()

    ## @brief gets a key's value from the session
    # @param key str
    # @return unknown
    def get_key(self, key):
        return getattr(object=self, name=key, default=None)

    ## @brief deletes a given key in the session
    # @param key str
    def delete_key(self, key):
        delattr(p_object=self, key)
        self.save()







'''
class SessionStore(ABC):

    expiration_limit = 900

    _instance = None

    def __init__(self, session_class=Session):
        self.session_class = session_class
        if self.__class__._instance is None:
            self.__class__._instance = self.__class__()

    def __getattr__(self, item):
        return getattr(self.__class__._instance, item)

    ## @brief Generates a session unique ID
    # @param cls
    # @param salt str
    # @return str
    @classmethod
    def generate_new_sid(cls, salt=None):
        return generate_key(salt)

    ## @brief Creates a new session
    # @param content dict : session content (default: {})
    # @return str
    def create_new_session(self, content={}):
        sid = self.__class__.generate_new_sid()
        self.save_session(sid, content)
        return sid

    ## @brief Destroys a session
    # @param sid str : session id
    @abstractmethod
    def delete_session(self, sid):
        pass

    ## @brief Reads a session content
    # @param sid str : session id
    # @return dict
    @abstractmethod
    def read_session(self, sid):
        return {}

    ## @brief saves a session to a file
    # @param sid str : session id
    # @param session dict : content to be saved
    @abstractmethod
    def save_session(self, sid, session):
        pass

    ## @brief lists all the sessions ids
    # @return list
    @abstractmethod
    def list_all_sessions(self):
        return []

    ## @brief cleans the session store's by destroying the expired sessions
    def clean(self):
        sessions_list = self.list_all_sessions()
        for sid in sessions_list:
            if self.has_session_expired(sid):
                self.delete_session(sid)

    ## @brief checks if a session exists
    # @param sid str : session id
    # @return bool
    @abstractmethod
    def is_session_existing(self, sid):
        return True

    ## @brief gets a session's last modified timestamp
    # @param sid str: session id
    # @return float
    @abstractmethod
    def get_session_last_modified(self, sid):
        pass

    ## @brief checks if a session has expired
    # @param sid str: session id
    # @return bool
    def has_session_expired(self, sid):
        session_last_modified = self.get_session_last_modified(sid)
        expiration_timestamp = session_last_modified + self.expiration_limit
        now_timestamp = get_utc_timestamp()
        return now_timestamp > expiration_timestamp

    ## @brief updates a session's content
    # @param sid str : session's id
    # @param content dict : items to update with their new value
    def update_session(self, sid, content):
        session = self.get_session(sid)
        if session is not None:
            for key, value in content.items():
                if key != 'sid':
                    session[key] = value
            self.save_session(sid, session)
            return session
        else:
            session = self.create_new_session(content)
            return session

    ## @brief gets a session's content
    # @param sid str : id of the session to read
    # @return dict | None if no valid session if found
    def get_session(self, sid):
        if self.is_session_existing(sid):
            if not self.has_session_expired(sid):
                session = self.read_session(sid)
            else:
                self.delete_session(sid)
                session = None
        else:
            session = None

        return session
'''