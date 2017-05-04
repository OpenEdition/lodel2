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


from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

CONFSPEC = {
    'lodel2.webui': {
        'standalone': ( 'False',
                        Validator('string')),
        'listen_address': ( '127.0.0.1',
                            Validator('dummy')),
        'listen_port': (    '9090',
                            Validator('int')),
        'static_url': (     'http://127.0.0.1/static/',
                            Validator('regex', pattern =  r'^https?://[^/].*$')),
        'virtualenv': (None,
                       Validator('path', none_is_valid=True)),
        'uwsgicmd': ('/usr/bin/uwsgi', Validator('dummy')),
        'cookie_secret_key': ('ConfigureYourOwnCookieSecretKey', Validator('dummy')),
        'cookie_session_id': ('lodel', Validator('dummy')),
        'uwsgi_workers': (2, Validator('int'))
    },
    'lodel2.webui.sessions': {
        'directory': (  '/tmp',
                        Validator('path')),
        'expiration': ( 900,
                        Validator('int')),
        'file_template': (  'lodel2_%s.sess',
                            Validator('dummy')),
    }
}
