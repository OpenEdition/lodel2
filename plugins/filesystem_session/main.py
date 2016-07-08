# -*- coding: utf-8 -*-

import os
import pickle
import uuid

from lodel.auth.exceptions import AuthenticationError
from lodel.plugin import LodelHook
from lodel.settings import Settings
from lodel.utils.datetime import get_utc_timestamp

SESSION_FILES_BASE_DIR = Settings.sessions.directory
SESSION_FILES_TEMPLATE = Settings.sessions.file_template
SESSION_EXPIRATION_LIMIT = Settings.sessions.expiration


## @brief generates a new session id
def generate_new_sid():
    return uuid.uuid1()


## @brief gets the session file path, given a session id
# @param sid str : session id
# @return str
def get_session_file_path(sid):
    return os.path.join(SESSION_FILES_BASE_DIR, SESSION_FILES_TEMPLATE) % sid


## @brief saves the session content to a session file
# @param sid str: session id
# @param session dict : session content to be saved
def save_session(sid, session):
    session_file_path = get_session_file_path(sid)
    pickle.dump(session, open(session_file_path, "wb"))


## @brief checks if a session file has expired
# @param sid str : session id
# @return bool
def is_session_expired(sid):
    session_file = get_session_file_path(sid)
    if not os.path.isfile(session_file):
        raise AuthenticationError("No session file found for the sid : %s" % sid)

    expiration_timestamp = os.stat(session_file).st_mtime + SESSION_EXPIRATION_LIMIT
    now_timestamp = get_utc_timestamp()
    return now_timestamp >= expiration_timestamp


## @brief reads a session content
# @param sid str: session id
# @return dict
def get_session_content(sid):
    session_file_path = get_session_file_path(sid)
    return pickle.load(open(session_file_path), 'rb')


## @brief starts a new session and returns its sid
# @param caller *
# @param payload dict
# @return str
@LodelHook('session_start')
def start_session(caller, payload):
    sid = generate_new_sid()
    session_file = get_session_file_path(sid)
    session = dict()
    for key, value in payload.items():
        session[key] = value
    save_session(sid, session)
    return sid

## @brief stops a session
# @param caller *
# @param sid str : session id
@LodelHook('session_destroy')
def stop_session(caller, sid):
    session_file_path = get_session_file_path(sid)
    if os.path.isfile(session_file_path):
        os.unlink(session_file_path)
    else:
        raise AuthenticationError("No session file found for the sid %s" % sid)


## @brief reads a session content
# @param caller *
# @param sid str: session id
@LodelHook('session_load')
def read_session(caller, sid):
    session_file = get_session_file_path(sid)
    if os.path.isfile(session_file):
        if not is_session_expired(sid):
            session = get_session_content(sid)
        else:
            LodelHook.call_hook('session_stop', __file__, sid)
            session = {}
    else:
        raise AuthenticationError("No session file found for the sid %s" % sid)
    return session


## @brief deletes all old session files (expired ones)
# @param caller *
@LodelHook('session_clean')
def clean_sessions(caller):
    session_files_path = os.path.abspath(SESSION_FILES_BASE_DIR)
    session_files = [os.path.join(session_files_path, file_object) for file_object in os.listdir(session_files_path) if os.path.isfile(os.path.join(session_files_path, file_object))]
    now_timestamp = get_utc_timestamp()
    for session_file in session_files:
        last_modified = os.stat(session_file).st_mtime
        expiration_timestamp = last_modified + SESSION_EXPIRATION_LIMIT
        if now_timestamp > expiration_timestamp:
            os.unlink(session_file)

## @brief updates the content session
# @param caller *
# @param payload dict: datas to insert/update in the session
@LodelHook('update_session')
def update_session_content(caller, payload):
    if 'sid' in payload:
        sid = payload['sid']
        session = LodelHook.call_hook('session_load', __file__, sid)
        for key, value in payload.items():
            session[key] = value
        save_session(sid, session)
    else:
        raise AuthenticationError("Missing session id in the request")
