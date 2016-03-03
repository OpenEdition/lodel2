# -*- coding: utf-8 -*-
from werkzeug.contrib.sessions import FilesystemSessionStore
from Modules.Interface.web.router import get_controller
from Modules.Interface.web.LodelRequest import LodelRequest

session_store = FilesystemSessionStore(path='tmp', filename_template='lodel_%s.sess')


# WSGI Application
def application(env, start_response):
    request = LodelRequest(env)
    sid = request.cookies.get('sid')
    if sid is None:
        request.session = session_store.new()
        print('sid is None')
        print(request.session.sid)
    else:
        request.session = session_store.get(sid)
        print('sid existant')
        print(request.session['user'])
        print(request.session.sid)

    controller = get_controller(request)
    response = controller(request)
    if request.session.should_save:
        session_store.save(request.session)
        response.set_cookie('sid', request.session.sid)

    return response(env, start_response)
