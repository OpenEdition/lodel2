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

#Define a minimal confspec used by multisite loader
LODEL2_CONFSPECS = {
    'lodel2': {
        'debug': (True, Validator('bool'))
    },
    'lodel2.server': {
        'listen_address': ('127.0.0.1', Validator('dummy')),
        #'listen_address': ('', Validator('ip')), #<-- not implemented
        'listen_port': ( 1337, Validator('int')),
        'uwsgi_workers': (8, Validator('int')),
        'uwsgicmd': ('/usr/bin/uwsgi', Validator('dummy')),
        'virtualenv': (None, Validator('path', none_is_valid = True)),
    },
    'lodel2.logging.*' : {
        'level': (  'ERROR',
                    Validator('loglevel')),
        'context': (    False,
                        Validator('bool')),
        'filename': (   None,
                        Validator('errfile', none_is_valid = True)),
        'backupcount': (    10,
                            Validator('int', none_is_valid = False)),
        'maxbytes': (   1024*10,
                        Validator('int', none_is_valid = False)),
    },
    'lodel2.datasources.*': {
        'read_only': (False, Validator('bool')),
        'identifier': ( None, Validator('string')),
    }
}
