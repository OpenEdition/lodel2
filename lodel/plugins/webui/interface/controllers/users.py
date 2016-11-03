# -*- coding: utf-8 -*-
from .base import get_response
from ...exceptions import *
from ...client import WebUiClient as WebUiClient

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {'lodel.logger': 'logger'})

import leapi_dyncode as dyncode #TODO : handle this with context

##@brief These functions are called by the rules defined in ../urls.py
## Their goal is to handle the user authentication

##@brief Controller's function to login a user, the corresponding form is in interface/users
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
def signin(request):
    msg=''
    # The form send the login and password, we can authenticate the user
    if request.method == 'POST':
        login = request.form['inputLogin']
        WebUiClient.authenticate(login, request.form['inputPassword'])
        # We get the informations about the user
        uid=WebUiClient['__auth_user_infos']['uid']
        leoclass=WebUiClient['__auth_user_infos']['leoclass']
        query_filter=list()
        query_filter.append((leoclass.uid_fieldname()[0],'=', uid))
        user = leoclass.get(query_filter)
        return get_response('users/welcome.html', username = user[0].data('login'))
    else:
        return get_response('users/signin.html')
    
##@brief Controller's function to logout a user
# @param request : the request (get or post)
# @note the response is given in the login html page 
def signout(request):
    WebUiClient.destroy()
    return get_response('users/signin.html')
