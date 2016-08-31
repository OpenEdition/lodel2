# -*- coding: utf-8 -*-
from .base import get_response
from ...exceptions import *
from lodel import logger
import leapi_dyncode as dyncode

def signin(request):
    msg=''
    if request.method == 'POST':
        print('Welcome')
    else:
        return get_response('users/signin.html')

