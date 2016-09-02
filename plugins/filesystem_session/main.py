# -*- coding: utf-8 -*-
import binascii
import datetime
import os
import pickle
import re
import time

from lodel import logger
from lodel.auth.exceptions import ClientAuthenticationFailure
from lodel.settings import Settings

from .filesystem_session import FileSystemSession

__sessions = dict()


## @brief generates a new session token
# @return str
def generate_token():
    token = binascii.hexlify(os.urandom(Settings.sessions.tokensize//2))
    if token in __sessions.keys():
        token = generate_token()
    return token


## @brief checks the validity of a given session token
# @param token str
# @raise ClientAuthenticationFailure for invalid or not found session token
def check_token(token):
    if len(token) != Settings.sessions.tokensize:
        raise ClientAuthenticationFailure("Invalid token string")
    if token not in __sessions.keys():
        raise ClientAuthenticationFailure("No session found for this token")


def generate_file_path(token):
    return os.abspath(os.path.join(Settings.sessions.directory, Settings.sessions.file_template) % token)


def get_token_from_filepath(filepath):
    token_regex = re.compile(os.abspath(os.path.join(Settings.sessions.directory, Settings.sessions.file_template % '(?P<token>.*)')))
    token_search_result = token_regex.match(filepath)
    if token_search_result is not None:
        return token_search_result.groupdict()['token']
    return None


## @brief returns the session's last modification timestamp
# @param token str
# @return float
# @raise ValueError if the given token doesn't match with an existing session
def get_session_last_modified(token):
    if token in __sessions[token]:
        return os.stat(__sessions[token]).st_mtime
    else:
        raise ValueError("The given token %s doesn't match with an existing session")


## @brief returns the token of a new session
# @return str
def start_session():
    session = FileSystemSession(generate_token())
    session.path = generate_file_path()
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


def restore_session(token):
    check_token(token)
    logger.debug("Restoring session : %s" % token)
    if os.path.isfile(__sessions[token]):
        with open(__sessions[token], 'rb') as session_file:
            session = pickle.load(session_file)
        return session
    else:
        raise FileNotFoundError("Session file not foudn for the token %s" % token)


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


def gc():
    # Unregistered files in the session directory
    session_files_directory = os.abspath(Settings.sessions.directory)
    for session_file_path in [file_path for file_path in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_path))]:
        token = get_token_from_filepath(session_file_path)
        if token is None or token not in __sessions.keys():
            os.unlink(session_file_path)

    # Expired registered sessions
    for token in __sessions.keys():
        if os.path.isfile(__sessions[token]):
            now_timestamp = time.mktime(datetime.datetime.now().timetuple())
            if now_timestamp - get_session_last_modified(token) > Settings.sessions.expiration:
                destroy_session(token)


def set_value(token, key, value):
    session = restore_session(token)
    session[key] = value
    save_session(token, session)


def get_value(token, key):
    session = restore_session(token)
    return session[key]


def del_value(token, key):
    session = restore_session(token)
    if key in session:
        del(session[key])
