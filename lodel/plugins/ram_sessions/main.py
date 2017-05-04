# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import os
import copy
import binascii

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.settings': ['Settings'],
    'lodel.auth.exceptions': ['ClientError', 'ClientAuthenticationFailure',
        'ClientPermissionDenied', 'ClientAuthenticationError']})

__sessions = dict()

def __generate_token():
    return binascii.hexlify(os.urandom(Settings.sessions.tokensize//2))

def _check_token(token):
    if len(token) != Settings.sessions.tokensize:
        raise ClientAuthenticationFailure("Malformed session token")
    if token not in __sessions:
        raise ClientAuthenticationFailure("No session with this token")

def start_session():
    token = __generate_token()
    __sessions[token] = dict()
    _check_token(token)
    logger.debug("New session created")
    return token

def destroy_session(token):
    _check_token(token)
    del(__sessions[token])
    logger.debug("Session %s destroyed" % token)

def restore_session(token):
    _check_token(token)
    logger.debug("Restoring session : %s" %__sessions[token])
    return __sessions[token]

def save_session(token, datas):
    _check_token(token)
    __sessions[token] = copy.copy(datas)
    logger.debug("Session saved")

