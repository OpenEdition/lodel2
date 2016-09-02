# -*- coding: utf-8 -*-
from .base import get_response
from ...exceptions import *
from ...client import WebUiClient as WebUiClient

from lodel import logger
import leapi_dyncode as dyncode

def signin(request):
    msg=''
    if request.method == 'POST':
        WebUiClient.authenticate(request.form['inputLogin'], request.form['inputPassword'])
        uid=WebUiClient.session().datas['__auth_user_infos']['uid']
        leoclass=WebUiClient.session().datas['__auth_user_infos']['leoclass']
        query_filter=list()
        query_filter.append((leoclass.uid_fieldname()[0],'=', uid))
        user = leoclass.get(query_filter)
        return get_response('users/welcome.html', username = user[0].data('login'))
    else:
        return get_response('users/signin.html')

def signout(request):
    WebUiClient.destroy()
    return get_response('users/signin.html')