# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient

from lodel.settings.settings import Settings as settings

common_collections = {
    'object': 'objects',
    'relation': 'relation'
}

collection_prefix = {
    'relation': 'rel_',
    'object': 'class_'
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


## @brief gets the settings given a connection name
# @param connection_name str
# @return dict
# @todo Use the settings module to store the connections parameters
def get_connection_args(connnection_name='default'):
    return {'host': 'localhost', 'port': 28015, 'login': 'lodel_admin', 'password': 'lapwd', 'dbname': 'lodel'}


## @brief Creates a connection to a MongoDb Database
# @param connection_name str
# @return MongoClient
def mongodbconnect(connection_name):
    login, password, host, port, dbname = get_connection_args(connection_name)
    return connect(host, port, db_name, username, password)

def connection_string(host, port, db_name, username, password):
    return 'mongodb://%s:%s@%s:%s' % (login, password, host, port)

def connect(host, port, db_name, username, password):
    connection = MongoClient(
        connection_string(host, port, db_name, username, password))
    database = connection[dbname]
    return database



## @brief Returns a collection name given a EmClass
# @param class_object EmClass
# @return str
def object_collection_name(class_object):
    if not class_object.pure_abstract:
        class_parent = class_object.parents[0].uid
        collection_name = ("%s%s" % (collection_prefix['object'], class_parent)).lower()
    else:
        collection_name = ("%s%s" % (collection_prefix['object'], class_object.name)).lower()

    return collection_name

##@brief Determine a collection field name given a lodel2 fieldname
#@note For the moment this method only return the argument but EVERYWHERE
#in the datasource we should use this method to gather proper fieldnames
#@param fieldname str : A lodel2 fieldname
#@return A string representing a well formated mongodb fieldname
#@see mongo_filednames
def mongo_fieldname(fieldname):
    return fieldname
##@brief Same as mongo_fieldname but for list of fields
#
#A small utility function
#@param fieldnames iterable : contains str only
#@return a list of converted fildnames (str)
#@see mongo_fieldname
def mongo_filednames(fieldnames):
    return [mongo_fieldname(fname) for fname in fieldnames]

## @brief Returns a list of orting options
# @param query_filters_order list
# @return list
def parse_query_order(query_filters_order):
    return [    (field, LODEL_SORT_OPERATORS_MAP[direction])
                for field, direction in query_filters_order]
