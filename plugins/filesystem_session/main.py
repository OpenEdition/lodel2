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
# @return str
def generate_new_sid():
    new_sid = uuid.uuid1()
    return new_sid

## @brief gets the session file path corresponding to a session id
def get_session_file_path(sid):
    return os.path.join(SESSION_FILES_BASE_DIR, SESSION_FILES_TEMPLATE) % sid

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
    pickle.dump(session, open(session_file, "wb"))
    return sid


## @brief stops a session
# @param caller *
# @param sid str : session id
@LodelHook('session_stop')
def stop_session(caller, sid):
    session_file_path = get_session_file_path(sid)
    if os.path.isfile(session_file_path):
        os.unlink(session_file_path)
    else:
        raise AuthenticationError("No session file found for the sid : %s" % sid)


## @brief checks if a session file has expired
# @param sid str : session id
# @return bool
def is_session_file_expired(sid):
    session_file = get_session_file_path(sid)

    if not os.path.isfile(session_file):
        raise AuthenticationError("No session file found for the sid : %s" % sid)

    expiration_timestamp = os.stat(session_file).st_mtime + SESSION_EXPIRATION_LIMIT
    timestamp_now = get_utc_timestamp()
    return timestamp_now >= expiration_timestamp


## @brief reads a session content
# @param caller *
# @param sid str : session id
@LodelHook('session_load')
def read_session(caller, sid):
    session_file = get_session_file_path(sid)
    if os.path.isfile(session_file):
        if not is_session_file_expired(sid):
            session = pickle.load(open(session_file, "rb"))
        else:
            LodelHook.call_hook('session_stop', __file__, sid)
            session = {}
    else:
        raise AuthenticationError("No session file found for the sid : %s" % sid)

    return session


## @brief deletes all old session files (expired ones)
# @param caller *
@LodelHook('lodel_delete_old_session_files')
def delete_old_session_files(caller):
    session_files_path = os.path.abspath(SESSION_FILES_BASE_DIR)
    session_files = [os.path.join(session_files_path, file_object) for file_object in os.listdir(session_files_path) if os.path.isfile(os.path.join(session_files_path, file_object))]
    timestamp_now = get_utc_timestamp()

    for session_file in session_files:
        last_modified = os.stat(session_file).st_mtime
        expiration_timestamp = last_modified + SESSION_EXPIRATION_LIMIT
        if timestamp_now > expiration_timestamp:
            os.unlink(session_file)
