# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient

from lodel.settings.settings import Settings as settings

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


def connection_string(host, port, username, password):
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
    if port != None:
        ret += ':'+str(port)
    return ret

##@brief Return an instanciated MongoClient
#@param host str : hostname or ip
#@param port int : port
#@param username str | None: username
#@param password str|None : password
def connection(host, port, username, password):
    conn_str = connection_string(host, port, username, password)
    return MongoClient(conn_str)

##@brief Return a database cursor
#@param host str : hostname or ip
#@param port int : port
#@param db_name str : database name
#@param username str | None: username
#@param password str|None : password
def connect(host, port, db_name, username, password):
    conn = connection(host, port, username, password)
    database = conn[db_name]
    return database


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
