# -*- coding: utf-8 -*-

"""
from lodel.auth.exceptions import AuthenticationError
from lodel.plugin import LodelHook

from .filesystem_session_store import FileSystemSession

## @brief starts a new session and returns its sid
# @param caller *
# @param payload dict
# @return str
@LodelHook('session_start')
def start_session(caller, payload):
    new_session = FileSystemSession(content=payload)
    return new_session.sid

'''
## @brief destroys a session
# @param caller *
# @param sid str : session id
@LodelHook('session_destroy')
def stop_session(caller, sid):
    FileSystemSession.destroy(sid)
'''

## @brief reads a session content
# @param caller *
# @param sid str: session id
# @return FileSystemSession
@LodelHook('session_load')
def read_session(caller, sid):
    return FileSystemSession.load(sid)

'''
## @brief destroys all the old sessions (expired ones)
# @param caller *
@LodelHook('session_clean')
def clean_sessions(caller):
    FileSystemSession.clean()
'''
"""
