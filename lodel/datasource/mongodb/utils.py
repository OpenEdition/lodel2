# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient

from lodel.settings.settings import Settings as settings

common_collections = {
    'object': 'object',
    'relation': 'relation'
}

collection_prefix = {
    'relation': 'rel_',
    'object': 'class_'
}

LODEL_OPERATORS_MAP = {
    '=': {'name': '$eq', 'value_type': None},
    '<=': {'name': '$lte', 'value_type': None},
    '>=': {'name': '$gte', 'value_type': None},
    '!=': {'name': '$ne', 'value_type': None},
    '<': {'name': '$lt', 'value_type': None},
    '>': {'name': '$gt', 'value_type': None},
    'in': {'name': '$in', 'value_type': list},
    'not in': {'name': '$nin', 'value_type': list},
    'OR': {'name': '$or', 'value_type': list},
    'AND': {'name': '$and', 'value_type': list}
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


## @brief Creates a connection to a MongoDb database
def mongodbconnect(connection_name):
    connection_args = get_connection_args(connection_name)
    checked_connection_args = check_connection_args(connection_args)
    if len(checked_connection_args['errors']) > 0:
        raise MongoDbConnectionError("\r\n-".join(checked_connection_args['errors']))

    # connection arguments are parsed after the check
    login, password, host, port, dbname = checked_connection_args['params']

    # Connection creation
    connection_string = 'mongodb://%s:%s@%s:%s' % (login, password, host, port)
    connection = MongoClient(connection_string)

    # Setting the database
    database = connection[dbname]

    return database


## @brief gets the settings given a connection name
# @param connection_name str
# @return dict
# @todo Use the settings module to store the connections parameters
def get_connection_args(connnection_name='default'):
    return {'host': 'localhost', 'port': 28015, 'login': 'lodel_admin', 'password': 'lapwd', 'dbname': 'lodel'}


## @brief Checks the settings given a connection name
# @param connection_args dict
# @return dict
# @throw MongoDbDataSourceError with the list of all the found errors
# @todo optimize the error management
def check_connection_args(connection_args):
    check_result = {'params': connection_args, 'errors': []}
    for connection_arg in MANDATORY_CONNECTION_ARGS:
        if connection_arg not in connection_args:
            check_result['errors'].append('Datasource connection error: %s parameter is missing.' % connection_arg)
    return check_result


## @brief Returns a collection name given a Emclass
# @param class_object EmClass
# @return str
def object_collection_name(class_object):
    if class_object.pure_abstract == False:
        class_parent = class_object.parents[0].uid
        collection_name = ("%s%s" % (collection_prefix['object'], class_parent)).lower()
    else:
        collection_name = ("%s%s" % (collection_prefix['object'], class_object.name)).lower()

    return collection_name


## @brief converts the query filters into MongoDB filters
# @param query_filters list : list of query_filters as tuples or dicts
# @param as_list bool : defines if the output will be a list (default: False)
# @return dict|list
# @todo refactor this function by adding a return_type argument (default= dict) which can be a dict or a list, then delete the convert_filter_list function
def parse_query_filters(query_filters, as_list=False):
    parsed_filters = dict() if not as_list else list()
    for query_filter in query_filters:
        if isinstance(query_filter, tuple):
            if as_list:
                parsed_filters.append(convert_filter(query_filter))
            else:
                parsed_filters.update(convert_filter(query_filter))
        elif isinstance(query_filter, dict):
            query_item = list(query_filter.items())[0]
            key = LODEL_OPERATORS_MAP[query_item[0]]
            if as_list:
                parsed_filters.append({key: parse_query_filters(query_item[1], as_list=True)})
            else:
                parsed_filters.update({key: parse_query_filters(query_item[1], as_list=True)})
        else:
            # TODO Add an exception management here in case the filter is neither a tuple nor a dict
            pass
    return parsed_filters


## @brief converts a Lodel query filter into a MongoDB filter
# @param filter_params tuple : (FIELD, OPERATOR, VALUE) representing the query filter to convert
# @return dict : {KEY: {OPERATOR:VALUE}}
# @todo Add an error management for the operator mismatch
def convert_filter(filter_params):
    key, operator, value = filter_params
    if operator not in ('like', 'not like'):
        if operator == 'in' and not isinstance(value, list):
            raise ValueError('A list should be used as value for an IN operator, %s given' % value.__class__)

        converted_operator = LODEL_OPERATORS_MAP[operator]['name']
        converted_filter = {key: {converted_operator: value}}
    else:
        converted_filter = convert_like_filter(filter_params)
    return converted_filter


## @brief Returns a list of sorting options
# @param query_filters_order list
# @return list
def parse_query_order(query_filters_order):
    ordering = list()
    for query_filter_order in query_filters_order:
        field, direction = query_filter_order
        ordering.append((field, LODEL_SORT_OPERATORS_MAP[direction]))
    return ordering


## @brief Converts "like" and "not like" filters into MongotDb filters
# @param like_filter tuple
# @return dict
def convert_like_filter(like_filter):
    key, operator, value = like_filter

    is_starting_with = value.endswith('*')
    is_ending_with = value.startswith('*')

    if is_starting_with and not is_ending_with:
        regex_pattern = value.replace('*', '^')
    elif is_ending_with and not is_starting_with:
        regex_pattern = value.replace('*', '$')
    elif is_starting_with and is_ending_with:
        regex_pattern = '%s' % value
    else:
        regex_pattern = '^%s$' % value

    regex_condition = {'$regex': regex_pattern, '$options': 'i'}
    converted_filter = {key: regex_condition}
    if operator.startswith('not'):
        converted_filter = {key: {'$not': regex_condition}}

    return converted_filter


## @brief identifier escaping
# @param idname str: An identifier
# @return str
def escape_idname(idname):
    if '`' in idname:
        raise ValueError("Invalid name : '%s'" % idname)
    return '`%s`' % idname

