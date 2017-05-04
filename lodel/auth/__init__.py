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


##@package lodel.auth Package handling authentication on Lodel2
#
#The authentication mechanism is divided in multiple pieces :
#- The client ( @ref lodel.auth.auth.Client ) singleton class that stores
# and uses the clients' informations
#- The session handler, implemented as a plugin
#
#@par Client class
#
#The @ref lodel.auth.auth.Client class is an abstract singleton. It is designed
#to be implemented by UI plugins. In fact we don't have the same client
#informations on a web UI, on a CLI or with UDP communications. The main goal
#of this class is then to provide an API to interface plugins to stores client
#informations allowing lodel2 to produce security log messages containing 
#client informations.
#
#@par Session handler
#
# The session handler is implemented as a plugin, called by hooks.
