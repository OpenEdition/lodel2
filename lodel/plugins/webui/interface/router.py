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


import re

from .controllers import *
from .urls import urls
from ..main import root_url

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings': ['Settings']})

def format_url_rule(url_rule):
    if url_rule.startswith('^'):
        res = url_rule.replace('^', '^'+root_url())
    else:
        res = root_url()+'.*'+url_rule
    return res


def get_controller(request):

    url_rules = []
    for url in urls:
        url_rules.append((format_url_rule(url[0]), url[1]))

    # Returning the right controller to call
    for regex, callback in url_rules:
        p = re.compile(regex)
        m = p.search(request.PATH)
        if m is not None:
            request.url_args = m.groupdict()
            return callback

    return not_found
