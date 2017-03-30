# -*- coding: utf-8 -*-

## @package lodel.plugins.filesystem_session.main Main entry point of the plugin

import binascii
import datetime
import os
import pickle
import re
import time

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.auth.exceptions': ['ClientAuthenticationFailure'],
    'lodel.settings': ['Settings']})

from .filesystem_session import FileSystemSession

__sessions = dict()

SESSION_TOKENSIZE = 150


## @brief generates a new session token
# @return str
def generate_token():
    token = binascii.hexlify(os.urandom(SESSION_TOKENSIZE//2))
    if token in __sessions.keys():
        token = generate_token()
    return token.decode('utf-8')


## @brief checks the validity of a given session token
# @param token str
# @throw ClientAuthenticationFailure for invalid or not found session token
def check_token(token):
    if len(token) != SESSION_TOKENSIZE:
        raise ClientAuthenticationFailure("Invalid token string")
    if token not in __sessions.keys():
        raise ClientAuthenticationFailure("No session found for this token")


## @brief returns a session file path for a specific token
# @param token str
# @return str
def generate_file_path(token):
    return os.path.abspath(os.path.join(Settings.sessions.directory, Settings.sessions.file_template) % token)


##
# @param filepath str
# @return str|None : returns the token or None if no token was found
def get_token_from_filepath(filepath):
    token_regex = re.compile(os.path.abspath(os.path.join(Settings.sessions.directory, Settings.sessions.file_template % '(?P<token>.*)')))
    token_search_result = token_regex.match(filepath)
    if token_search_result is not None:
        return token_search_result.groupdict()['token']
    return None


## @brief returns the session's last modification timestamp
# @param token str
# @return float
# @throw ValueError if the given token doesn't match with an existing session
def get_session_last_modified(token):
    if token in __sessions[token]:
        return os.stat(__sessions[token]).st_mtime
    else:
        raise ValueError("The given token %s doesn't match with an existing session")


## @brief returns the token of a new session
# @return str
def start_session():
    session = FileSystemSession(generate_token())
    session.path = generate_file_path(session.token)
    with open(session.path, 'wb') as session_file:
        pickle.dump(session, session_file)
    __sessions[session.token] = session.path
    logger.debug("New session created")
    return session.token


## @brief destroys a session given its token
# @param token str
def destroy_session(token):
    check_token(token)
    if os.path.isfile(__sessions[token]):
        os.unlink(__sessions[token])
        logger.debug("Session file for %s destroyed" % token)
    del(__sessions[token])
    logger.debug("Session %s unregistered" % token)


## @brief restores a session's content
# @param token str
# @return FileSystemSession|None
def restore_session(token):
    gc()
    check_token(token)
    logger.debug("Restoring session : %s" % token)
    if os.path.isfile(__sessions[token]):
        with open(__sessions[token], 'rb') as session_file:
            session = pickle.load(session_file)
        return session
    else:
        return None  # raise FileNotFoundError("Session file not found for the token %s" % token)


## @brief saves the session's content to a file
# @param token str
# @param datas dict
def save_session(token, datas):
    session = datas
    if not isinstance(datas, FileSystemSession):
        session = FileSystemSession(token)
        session.path = generate_file_path(token)
        session.update(datas)

    with open(__sessions[token], 'wb') as session_file:
        pickle.dump(session, session_file)

    if token not in __sessions.keys():
        __sessions[token] = session.path

    logger.debug("Session %s saved" % token)


## @brief session store's garbage collector
def gc():
    # Unregistered files in the session directory
    session_files_directory = os.path.abspath(Settings.sessions.directory)
    for session_file in [file_path for file_path in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_path))]:
        session_file_path = os.path.join(session_files_directory, session_file)
        token = get_token_from_filepath(session_file_path)
        if token is None or token not in __sessions.keys():
            os.unlink(session_file_path)
            logger.debug("Unregistered session file %s has been deleted" % session_file)

    # Expired registered sessions
    for token in __sessions.keys():
        if os.path.isfile(__sessions[token]):
            now_timestamp = time.mktime(datetime.datetime.now().timetuple())
            if now_timestamp - get_session_last_modified(token) > Settings.sessions.expiration:
                destroy_session(token)
                logger.debug("Expired session %s has been destroyed" % token)


##
# @param token str
# @param key str
# @param value
def set_session_value(token, key, value):
    session = restore_session(token)
    session[key] = value
    save_session(token, session)

##
# @param token str
# @param key str
def get_session_value(token, key):
    session = restore_session(token)
    return session[key]

##
# @param token str
# @param key str
def del_session_value(token, key):
    session = restore_session(token)
    if key in session:
        del(session[key])
