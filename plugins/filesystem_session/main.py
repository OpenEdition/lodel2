# -*- coding: utf-8 -*-

import binascii
import copy
import datetime
import os
import pickle
import re
import time

from lodel import logger
from lodel.settings import Settings
from lodel.auth.exceptions import ClientAuthenticationFailure

from .filesystem_session import FileSystemSession

## @brief lists the active sessions in a dict
# Its keys are the session tokens and its values are the file paths of session 
# files.
__sessions = dict()

# ====== UTILS ====== # 

## @brief Generates a session token
# @return str
def __generate_token():
    new_token = binascii.hexlify(os.urandom(Settings.sessions.tokensize//2))
    if new_token in __sessions.keys():
        new_token = __generate_token()
    return new_token

## @brief Checks if a token is valid and matchs with a registered session
# @param token str
# @raise ClientAuthenticationFailure for invalid or not found session token
def _check_token(token):
    # Bad length
    if len(token) != Settings.sessions.tokensize:
        raise ClientAuthenticationFailure("Malformed session token")
    # Not found
    if token not in __sessions:
        raise ClientAuthenticationFailure("No session found with this token")


## @brief Lists all the session files' paths
# @return list
def _list_all_sessions():
    session_files_directory = os.abspath(Settings.sessions.directory)
    return [file_path for file_path in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_path))]


## @brief Returns the token from a session file's name
# @param filename str
# @return str
def _get_token_from_session_filename(filename):
    token_regex = re.compile(Settings.sessions.file_template % '(?P<token>.*)')
    token_searching_result = token_regex.match(filename)
    if token_searching_result is not None:
        return token_searching_result.groupdict()['token']
    return None


## @brief Returns the session's last modification timestamp
# @param token str
# @return float
def _get_session_last_modified(token):
    if token in __sessions.keys():
        return os.stat(__sessions[token]).st_mtime
    else:
        raise ValueError("The given token %s doesn't match with an existing session")

# ====== SESSION MANAGEMENT ====== #
## @brief Registers the session in the active sessions' list
# @param session LodelSession
def _register_session(token):
    __sessions[token] = os.path.join(Settings.sessions.directory, Settings.sessions.file_template % token)
    
    
## @brief Session store's garbage collector
def gc():
    # unregistered files in the session directory
    sessions_dir_files = _list_all_sessions()
    for sessions_dir_file in sessions_dir_files:
        token = _get_token_from_session_filename(sessions_dir_file)
        if token is None or token not in __sessions.keys():
            os.unlink(sessions_dir_file)
    
    # expired registered sessions
    for token in __sessions.keys():
        if os.path.isfile(__sessions[token]):
            now_timestamp = time.mktime(datetime.datetime.now().timetuple())
            if now_timestamp - _get_session_last_modified(token) > Settings.sessions.expiration:
                destroy_session(token)


## @brief starts a new session and returns its token
# @return str
def start_session():
    new_token = __generate_token()
    new_session = FileSystemSession(new_token)
    new_session.save()
    _register_session(new_token)
    _check_token(new_token)
    logger.debug("New session created")
    return new_token


## @brief destroys a session defined by its token
# @param token str
def destroy_session(token):
    _check_token(token)
    if os.path.isfile(__sessions[token]):
        os.unlink(__sessions[token])
    del(__sessions[token])
    logger.debug("Session %s destroyed" % token)


## @brief restores a session's content
# @param token str
# @return FileSystemSession
def restore_session(token):
    _check_token(token)
    logger.debug("Restoring session : %s" % token)
    if os.path.isfile(__sessions[token]):
        with open(__sessions[token], 'rb') as session_file:
            session = pickle.load(session_file)
        return session
    return None


def save_session(token, datas=None):
    _check_token(token)
    session = restore_session(token)
    session.datas = copy.copy(datas)
    with open(__sessions[token], 'wb') as session_file:
        pickle.dump(session, session_file)
    logger.debug("Session %s saved" % token)
