# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from .base import get_response
from ...exceptions import *
from ...client import WebUiClient as WebUiClient

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {'lodel.logger': 'logger'})
LodelContext.expose_dyncode(globals(), 'dyncode')

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
