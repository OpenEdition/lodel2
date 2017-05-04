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
LodelContext.expose_modules(globals(), {'lodel.auth.client': ['Client']})

class WebUiClient(Client):
    
    def __init__(self, ip, user_agent, session_token = None):
        self.__ip = ip
        self.__user_agent = user_agent
        super().__init__(session_token = session_token)

    def __str__(self):
        return "%s (%s)" % (self.__ip, self.__user_agent)
