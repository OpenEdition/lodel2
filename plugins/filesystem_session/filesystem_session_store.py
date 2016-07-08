# -*- coding: utf-8 -*-

import os
import pickle
import uuid

from lodel.auth.exceptions import AuthenticationError
from lodel.settings import Settings
from lodel.utils.datetime import get_utc_timestamp


class FileSystemSessionStore:

    ## @brief instanciates a FileSystemSessionStore
    # @param base_directory str : path to the base directory containing the session files (default: session.directory param of the settings)
    # @param file_name_template str : template for the session files name (default : session.file_template param of the settings)
    # @param expiration_limit int : duration of a session validity without any action made (defaut : session.expiration param of the settings)
    def __init__(self, base_directory=Settings.session.directory, file_name_template=Settings.session.file_template, expiration_limit=Settings.session.expiration):
        self.expiration_limit = expiration_limit
        self.base_directory = base_directory
        self.file_name_template = file_name_template

    # === CRUD === #

    ## @brief creates a new session and returns its id
    # @param content dict : session content
    # @return str
    def create_new_session(self, content={}):
        sid = FileSystemSessionStore.generate_new_sid()
        session_file_path = self.get_session_file_path(sid)
        session = content
        self.save_session(sid, session)
        return sid

    ## @brief delete a session
    # @param sid str : id of the session to be deleted
    def delete_session(self, sid):
        if self.is_session_existing(sid):
            os.unlink(self.get_session_file_path(sid))
        else:
            raise AuthenticationError("No session file found for the sid %s" % sid)

    ## @brief gets a session's content
    # @param sid str : id of the session to read
    def get_session(self, sid):
        if self.is_session_existing(sid):
            if not self.has_session_expired(sid):
                session = self.get_session(sid)
            else:
                self.delete_session(sid)
                session = {}
        else:
            raise AuthenticationError("No session file found for the sid %s" % sid)

        return session

    ## @brief updates a session's content
    # @param sid str : session's id
    # @param content dict : items to update with their new value
    def update_session(self, sid, content):
        session = self.get_session(sid)
        for key, value in content.items():
            if key != 'sid':
                session[key] = value
        self.save_session(sid, session)

    ## @brief lists all the session files paths
    # @return list
    def list_all_sessions(self):
        session_files_directory = os.path.abspath(self.base_directory)
        session_files_list = [os.path.join(session_files_directory, file_object) for file_object in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_object))]
        return session_files_list

    def clean(self):
        files_list = self.list_all_sessions()
        now_timestamp = get_utc_timestamp()
        for session_file in files_list:
            if self.has_session_file_expired(session_file):
                os.unlink(session_file)

    # === UTILS === #
    @classmethod
    def generate_new_sid(cls):
        return uuid.uuid1()

    ## @brief returns the file path for a given session id
    # @param sid str : session id
    # @return str
    def get_session_file_path(self, sid):
        return os.path.join(self.base_directory, self.file_name_template) % sid

    ## @brief saves a session to a file
    # @param sid str : session id
    # @param session dict : content to be saved
    def save_session(self, sid, session):
        session_file_path = self.get_session_file_path(sid)
        pickle.dump(session, open(session_file_path, "wb"))

    ## @brief checks if a session exists
    # @param sid str : session id
    # @return bool
    def is_session_existing(self, sid):
        session_file = self.get_session_file_path(sid)
        return os.path.is_file(session_file)

    ## @brief checks if a session has expired
    # @param sid str: session id
    # @return bool
    def has_session_expired(self, sid):
        session_file = self.get_session_file_path(sid)
        return self.has_session_file_expired(session_file)

    def has_session_file_expired(self, session_file):
        expiration_timestamp = os.stat(session_file).st_mtime + self.expiration_limit
        now_timestamp = get_utc_timestamp()
        return now_timestamp > expiration_timestamp