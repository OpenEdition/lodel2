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

# TODO Add these informations to the configuration options (lodel2.webui.cookies)
COOKIE_SESSION_ID = 'toktoken'
COOKIE_SESSION_HASH = 'nekotkot'
COOKIE_SESSION_HASH_SALT = ['salt1', 'salt2']
COOKIE_SESSION_HASH_ALGO = hashlib.sha512


##@brief Return a salted hash of a cookie
def cookie_hash(token):
    token = str(token)
    return COOKIE_SESSION_HASH_ALGO(token.encode()).hexdigest()
    return COOKIE_SESSION_HASH_ALGO(
        (COOKIE_SESSION_HASH_SALT[0]+token+COOKIE_SESSION_HASH_SALT[1]).encode()).hexdigest()
    

##@brief Load cookie from request
#@note Can produce security warning logs
#@param request
#@return None or a session token
def load_cookie(request):
    token = request.cookies.get(COOKIE_SESSION_ID)

    if token is None or len(token) == 0:
        return None
    token=token.encode()

    hashtok = request.cookies.get(COOKIE_SESSION_HASH)
    if hashtok is None:
        raise ClientAuthenticationFailure(
            WebUiClient, 'Bad cookies : no hash provided')
    if cookie_hash(token) != hashtok:
        raise ClientAuthenticationFailure(
            WebUiClient, 'Bad cookies : hash mismatch')
    return token


##@brief Properly set cookies and hash given a token
#@param response
#@param token str : the session token
def save_cookie(response, token):
    response.set_cookie(COOKIE_SESSION_ID, token)
    response.set_cookie(COOKIE_SESSION_HASH, cookie_hash(token))


def empty_cookie(response):
    response.set_cookie(COOKIE_SESSION_ID, '')
    response.set_cookie(COOKIE_SESSION_HASH, '')


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
