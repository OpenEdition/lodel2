# -*- coding: utf-8 -*-

import os
import pickle
import re

from lodel.auth.exceptions import AuthenticationError
from lodel.auth.session import SessionStore
from lodel.settings import Settings


class FileSystemSessionStore(SessionStore):

    ## @brief instanciates a FileSystemSessionStore
    # @param base_directory str : path to the base directory containing the session files (default: session.directory param of the settings)
    # @param file_name_template str : template for the session files name (default : session.file_template param of the settings)
    # @param expiration_limit int : duration of a session validity without any action made (defaut : session.expiration param of the settings)
    def __init__(self, base_directory=Settings.session.directory, file_name_template=Settings.session.file_template, expiration_limit=Settings.session.expiration):
        self.expiration_limit = expiration_limit
        self.base_directory = base_directory
        self.file_name_template = file_name_template

    # === CRUD === #

    ## @brief delete a session
    # @param sid str : id of the session to be deleted
    def delete_session(self, sid):
        if self.is_session_existing(sid):
            os.unlink(self.get_session_file_path(sid))
        else:
            raise AuthenticationError("No session file found for the sid %s" % sid)

    ## @brief reads the content of a session
    # @param sid str : session id
    def read_session(self, sid):
        session_file_path = self.get_session_file_path(sid)
        with open(session_file_path, 'rb') as session_file:
            session_content = pickle.load(session_file)
        return session_content

    ## @brief saves a session to a file
    # @param sid str : session id
    # @param session dict : content to be saved
    def save_session(self, sid, session):
        session_file_path = self.get_session_file_path(sid)
        with open(session_file_path, 'wb') as session_file:
            pickle.dump(session, session_file)


    # === UTILS === #
    ## @brief returns the session id from the filename
    # @param filename str : session file's name (not the complete path)
    # @return str
    # @raise AuthenticationError : in case the sid could not be found for the given filename
    def filename_to_sid(self,filename):
        sid_regex = self.file_name_template % '(?P<sid>.*)'
        sid_regex_compiled = re.compile(sid_regex)
        sid_searching_result = sid_regex_compiled.match(filename)
        if sid_searching_result is not None:
            return sid_searching_result.groupdict()['sid']
        else:
            raise AuthenticationError('No session id could be found for this filename')

    ## @brief lists all the session files paths
    # @return list
    def list_all_sessions(self):
        session_files_directory = os.path.abspath(self.base_directory)
        sid_list = [self.filename_to_sid(file_object) for file_object in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_object))]
        return sid_list

    ## @brief returns the file path for a given session id
    # @param sid str : session id
    # @return str
    def get_session_file_path(self, sid):
        return os.path.join(self.base_directory, self.file_name_template) % sid

    ## @brief checks if a session exists
    # @param sid str : session id
    # @return bool
    def is_session_existing(self, sid):
        session_file = self.get_session_file_path(sid)
        return os.path.is_file(session_file)

    ## @brief gets a session's last modified timestamp
    # @param sid str: session id
    # @return float
    def get_session_last_modified(self, sid):
        session_file = self.get_session_file_path(sid)
        return os.stat(session_file).st_mtime
