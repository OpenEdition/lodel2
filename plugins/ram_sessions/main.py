#-*- coding: utf-8 -*-
import os
import copy

from lodel import logger
from lodel.settings import Settings
from lodel.auth.exceptions import *

__sessions = dict()

def _check_token(token):
    if len(token) != Settings.sessions.token_size:
        raise ClientAuthenticationFailure("Malformed session token")
    if token not in __sessions:
        raise ClientAuthenticationFailure("No session with this token")

def start_session():
    token = os.urandom(Settings.sessions.token_size)
    __sessions[token] = dict()
    return token

def destroy_session(token):
    _check_token(token)
    del(__sessions[token])

def restore_session(token):
    _check_token(token)
    logger.debug("Restoring session : %s" %__sessions[token])
    return __sessions[token]

def save_session(token, datas):
    _check_token(token)
    __sessions[token] = copy.copy(datas)


def get_value(token, name):
    _check_token(token)
    return __sessions[token][name]

def del_value(token, name):
    _check_token(token)
    if name in __sessions[token]:
        del(__sessions[token][name])

