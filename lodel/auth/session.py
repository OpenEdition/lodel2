# -*- coding; utf-8 -*-

from abc import ABC, abstractmethod
from uuid import uuid1

from lodel.auth.exceptions import AuthenticationError
from lodel.utils.datetime import get_utc_timestamp


class SessionStore(ABC):

    expiration_limit = 900

    ## @brief Generates a session unique ID
    # @param cls
    # @return str
    @classmethod
    def generate_new_sid(cls):
        return uuid1()

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
        for key, value in content.items():
            if key != 'sid':
                session[key] = value
        self.save_session(sid, session)

    ## @brief gets a session's content
    # @param sid str : id of the session to read
    # @return dict
    def get_session(self, sid):
        if self.is_session_existing(sid):
            if not self.has_session_expired(sid):
                session = self.read_session(sid)
            else:
                self.delete_session(sid)
                session = {}
        else:
            raise AuthenticationError("No session file found for the sid %s" % sid)

        return session
