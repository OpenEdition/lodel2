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


from lodel.context import LodelContext

if not LodelContext.is_initialized():
    import loader # Lodel2 loader

import os
import hashlib
import time
import sys

from werkzeug.wrappers import Response

LodelContext.expose_modules(globals(), {
    'lodel.settings': ['Settings'],
    'lodel.logger': 'logger',
    'lodel.auth.exceptions': ['ClientError', 'ClientAuthenticationFailure',
        'ClientPermissionDenied', 'ClientAuthenticationError']})

from .interface.router import get_controller
from .interface.lodelrequest import LodelRequest
from .exceptions import *
from .client import WebUiClient

try:
    SESSION_FILES_BASE_DIR = Settings.webui.sessions.directory
    SESSION_FILES_TEMPLATE = Settings.webui.sessions.file_template
    SESSION_EXPIRATION_LIMIT = Settings.webui.sessions.expiration


    COOKIE_SECRET_KEY = bytes(Settings.webui.cookie_secret_key, 'utf-8')
    COOKIE_SESSION_ID = Settings.webui.cookie_session_id
except Exception as e:
    print("Fails to start : ", e, file=sys.stderr)
    exit(1)

from werkzeug.contrib.securecookie import SecureCookie

def load_cookie(request):
    datas = request.cookies.get(COOKIE_SESSION_ID)

    if not datas:
        return None

    cookie_content = SecureCookie.unserialize(datas, COOKIE_SECRET_KEY)

    if 'token' not in cookie_content:
        return None

    token = cookie_content['token']

    if token is None or len(token) == 0:
        return None

    return token


def save_cookie(response, token):
    response.set_cookie(COOKIE_SESSION_ID, SecureCookie({'token': token}, COOKIE_SECRET_KEY).serialize())


def empty_cookie(response):
    response.set_cookie(COOKIE_SESSION_ID, '')

#Starting instance
try:
    loader.start() #Works only in MONOSITE mode
except NameError:
    pass
#providing access to dyncode


# WSGI Application
def application(env, start_response):
    request = LodelRequest(env)
    session_token = None
    try:
        #We have to create the client before restoring cookie in order to be able
        #to log messages with client infos
        client = WebUiClient(env['REMOTE_ADDR'], env['HTTP_USER_AGENT'], None)
        session_token = load_cookie(request)
        if session_token is not None and len(session_token) > 0:
            WebUiClient.restore_session(session_token)
        session_token = None
        
        try:
            controller = get_controller(request)
            logger.debug(controller)
            response = controller(request)
        except HttpException as e:
            try:
                response = e.render(request)
            except Exception as eb:
                raise eb
                res = Response()
                res.status_code = 500
                return res
        session_token = WebUiClient.session_token()
        if session_token is not None:
            save_cookie(response, session_token)
        session_token = None
    except (ClientError, ClientAuthenticationError):
        response = HttpException(200).render(request)
        empty_cookie(response)
    except ClientAuthenticationFailure:
        response = HttpException(200).render(request)
        empty_cookie(response)
    except Exception as e:
        raise e

    res = response(env, start_response)

    WebUiClient.clean()
    return res
