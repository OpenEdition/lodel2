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


import pymongo
from pymongo import MongoClient

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.settings': [('Settings', 'settings')],
    'lodel.logger': 'logger'})

common_collections = {
    'object': 'objects',
    'relation': 'relation'
}

LODEL_SORT_OPERATORS_MAP = {
    'ASC': pymongo.ASCENDING,
    'DESC': pymongo.DESCENDING
}

MONGODB_SORT_OPERATORS_MAP = {
    'ASC': 1,
    'DESC': -1
}

MANDATORY_CONNECTION_ARGS = ('host', 'port', 'login', 'password', 'dbname')


class MongoDbConnectionError(Exception):
    pass

##@brief Forge a mongodb uri connection string
#@param host str : hostname
#@param port int|str : port number
#@param username str
#@param password str
#@param db_name str : the db to authenticate on (mongo as auth per db)
#@param ro bool : if True open a read_only connection
#@return a connection string
#@see https://docs.mongodb.com/v2.4/reference/connection-string/#connection-string-options
#@todo escape arguments
def connection_string(host, port, username, password, db_name = None, ro = None):
    ret = 'mongodb://'
    if username != None:
        ret += username
        if password != None:
            ret += ':'+password
        ret+='@'
    elif password != None:
        raise RuntimeError("Password given but no username given...")
    host = 'localhost' if host is None else host
    ret += host
    if port is not None:
        ret += ':'+str(port)
    if db_name is not None:
        ret += '/'+db_name
    else:
        logger.warning("No database indicated. Huge chance for authentication \
to fails")
    if ro:
        ret += '?readOnly='+str(bool(ro))
    return ret

##@brief Return an instanciated MongoClient from a connstring
#@param connstring str : as returned by connection_string() method
#@return A MongoClient instance
def connect(connstring):
    return MongoClient(connstring)

## @brief Returns a collection name given a EmClass
# @param class_object EmClass
# @return str
def object_collection_name(class_object):
    return class_object.__name__

def collection_name(class_name):
    return class_name

## @brief Determine a collection field name given a lodel2 fieldname
# @note For the moment this method only return the argument but EVERYWHERE
# in the datasource we should use this method to gather proper fieldnames
# @param fieldname str : A lodel2 fieldname
# @return A string representing a well formated mongodb fieldname
# @see mongo_filednames
def mongo_fieldname(fieldname):
    return fieldname


## @brief Same as mongo_fieldname but for list of fields
#
# A small utility function
# @param fieldnames iterable : contains str only
# @return a list of converted fildnames (str)
# @see mongo_fieldname
def mongo_fieldnames(fieldnames):
    return [mongo_fieldname(fname) for fname in fieldnames]


## @brief Returns a list of orting options
# @param query_filters_order list
# @return list
def parse_query_order(query_filters_order):
    return [(field, LODEL_SORT_OPERATORS_MAP[direction])
            for field, direction in query_filters_order]
