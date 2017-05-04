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


class LodelException(Exception):
    pass

class LodelExceptions(LodelException):
    ##@brief Instanciate a new exceptions handling multiple exceptions
    # @param msg str : Exception message
    # @param exceptions dict : A list of data check Exception with concerned field (or stuff) as key
    def __init__(self, msg = "Unknow error", exceptions = None):
        self._msg = msg
        self._exceptions = dict() if exceptions is None else exceptions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = self._msg
        for_iter = self._exceptions.items() if isinstance(self._exceptions, dict) else enumerate(self.__exceptions)
        for obj, expt in for_iter:
            msg += "\n\t{expt_obj} : ({expt_name}) {expt_msg}; ".format(
                    expt_obj = obj,
                    expt_name=expt.__class__.__name__,
                    expt_msg=str(expt)
            )
        return msg

##@brief Designed to be a non catched exception.
#
#@note Designed to be raised in dramatic case
class LodelFatalError(Exception):
    pass

##@brief Designed to be a catched exception.
#
#@note Designed to be raised in DataHandler
class DataNoneValid(Exception):
    pass
    
##@brief Designed to be a catched exception.
#
#@note Designed to be raised in DataHandler
class FieldValidationError(Exception):
    pass

