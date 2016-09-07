# -*- coding: utf-8 -*-
import loader # Lodel2 loader

import os
import hashlib
import time

from werkzeug.wrappers import Response

from lodel.settings import Settings
from .interface.router import get_controller
from .interface.lodelrequest import LodelRequest
from .exceptions import *
from .client import WebUiClient
from lodel.auth.exceptions import *

SESSION_FILES_BASE_DIR = Settings.webui.sessions.directory
SESSION_FILES_TEMPLATE = Settings.webui.sessions.file_template
SESSION_EXPIRATION_LIMIT = Settings.webui.sessions.expiration


COOKIE_SECRET_KEY = bytes(Settings.webui.cookie_secret_key, 'utf-8')
COOKIE_SESSION_ID = Settings.webui.cookie_session_id

from werkzeug.contrib.securecookie import SecureCookie

def load_cookie(request):
    datas = request.cookies.get(COOKIE_SESSION_ID)
    if not datas:
        return None
    cookie_content = SecureCookie.unserialize(datas, COOKIE_SECRET_KEY)
    token = cookie_content['token']
    if token is None or len(token) == 0:
        return None
    return token


def save_cookie(response, token):
    response.set_cookie(COOKIE_SESSION_ID, SecureCookie({'token': token}, COOKIE_SECRET_KEY).serialize())


def empty_cookie(response):
    response.set_cookie(COOKIE_SESSION_ID, '')

#Starting instance
loader.start()
#providing access to dyncode
import lodel
import leapi_dyncode as dyncode
lodel.dyncode = dyncode


# WSGI Application
def application(env, start_response):
    request = LodelRequest(env)
    session_token = None
    try:
        #We have to create the client before restoring cookie in order to be able
        #to log messages with client infos
        client = WebUiClient(env['REMOTE_ADDR'], env['HTTP_USER_AGENT'], None)
        session_token = load_cookie(request)
        if session_token is not None:
            WebUiClient.restore_session(session_token)
            #next line is for testing purpose
            print("ACCESS DATAS : ", WebUiClient['last_request'])
        session_token = None
        #next line is for testing purpose
        WebUiClient['last_request'] = time.time()
        
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
