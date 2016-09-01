# -*- coding: utf-8 -*-
from .base import get_response
from ...exceptions import *
from ...client import WebUiClient as WebUiClient
from lodel.auth.client import LodelSession as Session
from lodel import logger
import leapi_dyncode as dyncode

def signin(request):
    msg=''
    if request.method == 'POST':
        WebUiClient.authenticate(request.form['inputLogin'], request.form['inputPassword'])
        logger.debug(WebUiClient.session().datas)
        uid=WebUiClient.session().datas['__auth_user_infos']['uid']
        leoclass=WebUiClient.session().datas['__auth_user_infos']['leoclass']
        query_filter=list()
        query_filter.append((leoclass.uid_fieldname()[0],' = ', uid))
        username = leoclass.get(query_filter)
        return get_response('users/welcome.html', username = username)
    else:
        return get_response('users/signin.html')

