# -*- coding: utf-8 -*-

from lodel.plugin import LodelHook

from .filesystem_session_store import FileSystemSession

## @brief starts a new session and returns its sid
# @param caller *
# @param payload dict
# @return str
def start_session():
    new_session = FileSystemSession()
    return new_session.sid

## @brief destroys a session
# @param caller *
# @param sid str : session id
def destroy_session(sid):
    FileSystemSession.destroy(sid)

## @brief reads a session content
# @param caller *
# @param sid str: session id
# @return FileSystemSession
def restore_session(sid):
    return FileSystemSession.load(sid)

##@brief Set a session value
#@param name str : session variable name
#@param value mixed : session variable value
def set_value(name, value):
    pass

##@brief Get a session value
#@param name str : the session variable name
#@return the value
def get_value(name):
    pass

##@brief Delete a session value
#@param name str : the session variable name
def del_value(name):
    pass
    
