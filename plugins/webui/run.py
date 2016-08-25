# -*- coding: utf-8 -*-
import loader # Lodel2 loader

import os
import hashlib
import time

from werkzeug.contrib.sessions import FilesystemSessionStore
from werkzeug.wrappers import Response
from werkzeug.contrib.securecookie import SecureCookie

from lodel.settings import Settings
from .interface.router import get_controller
from .interface.lodelrequest import LodelRequest
from .exceptions import *
from .client import WebUiClient
from lodel.auth.exceptions import *
from lodel.utils.datetime import get_utc_timestamp
from lodel.plugin.hooks import LodelHook

SESSION_FILES_BASE_DIR = Settings.webui.sessions.directory
SESSION_FILES_TEMPLATE = Settings.webui.sessions.file_template
SESSION_EXPIRATION_LIMIT = Settings.webui.sessions.expiration

session_store = FilesystemSessionStore(path=SESSION_FILES_BASE_DIR, filename_template=SESSION_FILES_TEMPLATE)

COOKIE_SESSION_ID = 'toktoken'
COOKIE_SESSION_HASH = 'nekotkot'
COOKIE_SESSION_HASH_SALT = [ os.urandom(32) for _ in range(2) ] #Before and after salt (maybe useless)
COOKIE_SESSION_HASH_ALGO = hashlib.sha512

##@brief Return a salted hash of a cookie
def cookie_hash(token):
    return COOKIE_SESSION_HASH_ALGO(
        COOKIE_SESSION_HASH_SALT[0]+token+COOKIE_SESSION_HASH_SALT[1]).hexdigest()
    

##@brief Load cookie from request
#@note Can produce security warning logs
#@param request
#@return None or a session token
def load_cookie(request):
    token = request.cookies.get(COOKIE_SESSION_ID)
    if token is None and token != '':
        return None
    token = bytes(token, 'utf-8')
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

# TODO déplacer dans un module "sessions.py"
def delete_old_session_files(timestamp_now):
    session_files_path = os.path.abspath(session_store.path)
    session_files = [os.path.join(session_files_path, file_object) for file_object in os.listdir(session_files_path)
                     if os.path.isfile(os.path.join(session_files_path, file_object))]

    for session_file in session_files:
        last_modified = os.stat(session_file).st_mtime
        expiration_timestamp = last_modified + SESSION_EXPIRATION_LIMIT
        if timestamp_now > expiration_timestamp:
            os.unlink(session_file)


def is_session_file_expired(timestamp_now, sid):
    session_file = session_store.get_session_filename(sid)
    expiration_timestamp = os.stat(session_file).st_mtime + SESSION_EXPIRATION_LIMIT
    if timestamp_now < expiration_timestamp:
        return False
    return True


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
            WebClient.restore_session(token)
        session_token = None
        #test
        WebUiClient['last_request'] = time.time()
        try:
            controller = get_controller(request)
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
            save_cookie(response,session_token)
        session_token = None
            

    except (ClientError, ClientAuthenticationError):
        response = HttpException(400).render(request)
        empty_cookie(response)
    except ClientAuthenticationFailure:
        response = HttpException(401).render(request)
        empty_cookie(response)
    except Exception as e:
        raise e

    res = response(env, start_response)

    WebUiClient.destroy()
    return res
