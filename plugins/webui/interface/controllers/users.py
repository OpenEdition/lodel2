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
        return get_response('users/welcome.html')
    else:
        return get_response('users/signin.html')

