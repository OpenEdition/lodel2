# -*- coding: utf-8 -*-
import loader # Lodel2 loader

import os
from werkzeug.contrib.sessions import FilesystemSessionStore
from werkzeug.wrappers import Response

from lodel.settings import Settings
from .interface.router import get_controller
from .interface.lodelrequest import LodelRequest
from .exceptions import *
from lodel.utils.datetime import get_utc_timestamp
from lodel.plugin.hooks import LodelHook

SESSION_FILES_BASE_DIR = Settings.webui.sessions.directory
SESSION_FILES_TEMPLATE = Settings.webui.sessions.file_template
SESSION_EXPIRATION_LIMIT = Settings.webui.sessions.expiration

session_store = FilesystemSessionStore(path=SESSION_FILES_BASE_DIR, filename_template=SESSION_FILES_TEMPLATE)

#Starting instance
loader.start()

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
    current_timestamp = get_utc_timestamp()
    delete_old_session_files(current_timestamp)
    request = LodelRequest(env)
    sid = request.cookies.get('sid')
    if sid is None or sid not in session_store.list():
        request.session = session_store.new()
        request.session['last_accessed'] = current_timestamp
    else:
        request.session = session_store.get(sid)
        if is_session_file_expired(current_timestamp, sid):
            session_store.delete(request.session)
            request.session = session_store.new()
            request.session['user_context'] = None
        request.session['last_accessed'] = current_timestamp
    
    try:
        controller = get_controller(request)
        response = controller(request)
    except HttpException as e:
        try:
            response = e.render(request)
        except Exception as eb:
            res = Response()
            res.status_code = 500
            return res
        
        
    if request.session.should_save:
        session_store.save(request.session)
        response.set_cookie('sid', request.session.sid)
    
    res = response(env, start_response)
    LodelHook.call_hook('lodel2_session_end', __file__, None)
    return res
