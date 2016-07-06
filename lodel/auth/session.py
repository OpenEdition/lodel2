# -*- coding: utf-8 -*-
from lodel.plugin import LodelHook


## @brief checks if a session is valid or not, given its id
# @param session_id str
# @return bool
@LodelHook('lodel2.check_session')
def check_session(session_id):
    return True


## @brief gets the session data corresponding to a session id
# @param session_id str
# @return dict|None : returns a dict containing the session data if a session is active/valid, None if not
def get_session(session_id):
    is_valid = LodelHook.call_hook('lodel2.check_session')
    session_data = dict()
    return session_data
