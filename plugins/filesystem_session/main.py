# -*- coding: utf-8 -*-

import os
from werkzeug.contrib.sessions import FilesystemSessionStore

from lodel.plugin import LodelHook
from lodel.settings import Settings
from lodel.utils.datetime import get_utc_timestamp

SESSION_FILES_BASE_DIR = Settings.sessions.directory
SESSION_FILES_TEMPLATE = Settings.sessions.file_template
SESSION_EXPIRATION_LIMIT = Settings.sessions.expiration

session_store = FilesystemSessionStore(path=SESSION_FILES_BASE_DIR, filename_template=SESSION_FILES_TEMPLATE)


@LodelHook('lodel_delete_old_session_files')
def delete_old_session_files(caller, timestamp_now):
    session_files_path = os.path.abspath(session_store.path)
    session_files = [os.path.join(session_files_path, file_object) for file_object in os.listdir(session_files_path) if os.path.isfile(os.path.join(session_files_path, file_object))]

    for session_file in session_files:
        last_modified = os.stat(session_file).st_mtime
        expiration_timestamp = last_modified + SESSION_EXPIRATION_LIMIT
        if timestamp_now > expiration_timestamp:
            os.unlink(session_file)


def is_session_file_expired(timestamp_now, sid):
    session_file = session_store.get_session_filename(sid)
    expiration_timestamp = os.stat(session_file).st_mtime + SESSION_EXPIRATION_LIMIT
    return timestamp_now >= expiration_timestamp


## @brief starts a new session
# @param caller *
# @param payload dict : dictionary containing the content of the session
@LodelHook('lodel_start_session')
def start_session(caller, payload):
    session = session_store.new()
    for key, value in payload.items():
        session[key] = value
    session_store.save(session)


## @brief reads the content of the session
# @param caller *
# @param sid str
# @return dict
@LodelHook('lodel_read_session')
def read_session(caller, sid):
    timestamp = get_utc_timestamp()
    session = None
    if not is_session_file_expired(timestamp, sid):
        session = session_store.get(sid)

    return session


@LodelHook('lodel_update_session')
def update_session(caller, timestamp_now, sid):
    if sid is None or sid not in session_store.list():
        session = session_store.new()
        session['last_accessed'] = timestamp_now
    else:
        session = session_store.get(sid)
        if is_session_file_expired(timestamp_now, sid):
            session_store.delete(session)
            session = session_store.new()
            session['user_context'] = None
        session['last_accessed'] = timestamp_now
