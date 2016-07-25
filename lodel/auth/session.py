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

    ## @brief lists all the sessions in the session store
    # @return list
    @classmethod
    @abstractmethod
    def list_all_sessions(cls):
        return []

    ## @brief checks if a given session id corresponds to an existing session
    # @param sid str: session id
    # @return bool
    @classmethod
    @abstractmethod
    def exists(cls, sid):
        return True
