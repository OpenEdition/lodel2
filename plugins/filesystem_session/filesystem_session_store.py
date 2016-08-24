# -*- coding: utf-8 -*-

import os
import pickle
import re

from lodel.auth.client import LodelSession
from lodel.settings import Settings


class FileSystemSession(LodelSession):

    __sessions = {}

    EXPIRATION_LIMIT = Settings.sessions.expiration
    BASE_DIRECTORY = Settings.sessions.directory
    FILENAME_TEMPLATE = Settings.sessions.file_template

    def __init__(self):
        self.path = None  # Is initialized in the store method
        super().__init__()

    ## @brief stores the session
    def store(self):
        self.path = self.__class__.generate_session_file_name(self.sid)
        self.save()

    ## @brief registers the session in the active sessions list
    def register_session(self):
        self.__class__.__sessions[self.sid] = self.path

    ## @brief saves the session
    # @todo security
    def save(self):
        with open(self.path, 'wb') as session_file:
            pickle.dump(self, session_file)

    ## @brief loads a session
    # @param sid str : session id
    # @return FileSystemSession
    @classmethod
    def load(cls, sid):
        if sid in cls.__sessions.keys():
            session_file_path = cls.__sessions[sid]
            with open(session_file_path, 'rb') as session_file:
                session = pickle.load(session_file)
            return session
        return None

    ## @brief cleans the session store
    # @todo add more checks
    @classmethod
    def clean(cls):
        # unregistered files in the session directory (if any)
        session_dir_files = cls.list_all_sessions()
        for session_dir_file in session_dir_files:
            sid = cls.filename_to_sid(session_dir_file)
            if sid is None or sid not in cls.__sessions.keys():
                os.unlink(session_dir_file)
        # registered sessions
        for sid in cls.__sessions.keys():
            if cls.is_expired(sid):
                cls.destroy(sid)

    ## @brief gets the last modified date of a session
    # @param sid str : session id
    @classmethod
    def get_last_modified(cls, sid):
        return os.stat(cls.__sessions[sid]).st_mtime

    ## @brief lists all the files contained in the session directory
    # @return list
    @classmethod
    def list_all_sessions(cls):
        session_files_directory = os.abspath(cls.BASE_DIRECTORY)
        files_list = [file_path for file_path in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_path))]
        return files_list

    ## @brief returns the session id from the filename
    # @param filename str : session file's name
    # @return str
    @classmethod
    def filename_to_sid(cls, filename):
        sid_regex = re.compile(cls.FILENAME_TEMPLATE % '(?P<sid>.*)')
        sid_searching_result = sid_regex.match(filename)
        if sid_searching_result is not None:
            return sid_searching_result.groupdict()['sid']
        return None

    ## @brief deletes a session's informations
    @classmethod
    def delete_session(cls, sid):
        if os.path.isfile(cls.__sessions[sid]):
            # Deletes the session file
            os.unlink(cls.__sessions[sid])

    ## @brief generates session file name
    # @param sid str : session id
    # @return str
    @classmethod
    def generate_session_file_name(cls, sid):
        return os.path.join(cls.BASE_DIRECTORY, cls.FILENAME_TEMPLATE) % sid

    ## @brief checks if a session exists
    # @param sid str: session id
    # @return bool
    @classmethod
    def exists(cls, sid):
        return cls.is_registered(sid) and (os.path.isfile(cls.__sessions[sid]))
