# -*- coding: utf-8 -*-

from lodel.auth.exceptions import AuthenticationError
from lodel.plugin import LodelHook

from .filesystem_session_store import FileSystemSessionStore

session_store = FileSystemSessionStore()


## @brief starts a new session and returns its sid
# @param caller *
# @param payload dict
# @return str
@LodelHook('session_start')
def start_session(caller, payload):
    return session_store.create_new_session(payload)


## @brief destroys a session
# @param caller *
# @param sid str : session id
@LodelHook('session_destroy')
def stop_session(caller, sid):
    session_store.delete_session(sid)


## @brief reads a session content
# @param caller *
# @param sid str: session id
# @return dict
@LodelHook('session_load')
def read_session(caller, sid):
    return session_store.get_session(sid)


## @brief destroys all the old sessions (expired ones)
# @param caller *
@LodelHook('session_clean')
def clean_sessions(caller):
    session_store.clean()


## @brief updates the content of the session
# @param caller *
# @param payload dict : datas to insert/update in the session
@LodelHook('update_session')
def update_session_content(caller, payload):
    if 'sid' in payload:
        sid = payload['sid']
        del payload['sid']
        session_store.update_session(sid, payload)
    else:
        raise AuthenticationError("Session Update: Missing sid (session id) in the given payload argument")
