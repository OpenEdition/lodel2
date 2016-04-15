# -*- coding: utf-8 -*-

import pymongo

collection_prefix = {
    'relation': 'rel_',
    'collection': 'class_'
}

LODEL_OPERATORS_MAP = {
    '=': {'name': '$eq', 'value_type': None},
    '<=': {'name': '$lte', 'value_type': None},
    '>=': {'name': '$gte', 'value_type': None},
    '!=': {'name': '$ne', 'value_type': None},
    '<': {'name': '$lt', 'value_type': None},
    '>': {'name': '$gt', 'value_type': None},
    ' in ': {'name': '$in', 'value_type': list},
    ' not in ': {'name': '$nin', 'value_type': list},
    ' like ': {'name': '$eq', 'value_type': str},
    ' not like ': {'name': '', 'value_type': str},  # TODO Add the operator
    'OR': {'name': '$or', 'value_type': list},
    'AND': {'name': '$and', 'value_type': list}
}

LODEL_SORT_OPERATORS_MAP = {
    'ASC': pymongo.ASCENDING,
    'DESC': pymongo.DESCENDING
}


## @brief Returns a collection name given a Emclass name
# @param class_name str : The class name
# @return str
def object_collection_name(class_name):
    return ("%s%s" % (collection_prefix['object'], class_name)).lower()


## @brief converts the query filters into MongoDB filters
# @param query_filters list
# @return dict
# @todo refactor this function by adding a return_type argument (default= dict) which can be a dict or a list, then delete the convert_filter_list function
def parse_query_filters(query_filters):
    filters_dict = dict()
    for query_filter in query_filters:
        if isinstance(query_filter, tuple):
            filters_dict.update(convert_filter(query_filter))
        elif isinstance(query_filter, dict):
            query_item = list(query_filter.items())[0]
            key = LODEL_OPERATORS_MAP[query_item[0]]
            filters_dict.update({key: convert_filter_list(query_item[1])})
        else:
            # TODO Add an exception management here in case the filter is neither a tuple nor a dict
            pass
    return filters_dict


## @brief converts a query filters list into MongoDB filters list
#   It is used mainly in case of an "AND" or an "OR"
# @param filters_list list
# @return list
def convert_filter_list(filters_list):
    converted_filters_list = list()
    for filter_list_item in filters_list:
        if isinstance(filter_list_item, tuple):
            converted_filters_list.append(convert_filter(filter_list_item))
        elif isinstance(filter_list_item, dict):
            query_item = list(filter_list_item.items())[0]
            key = LODEL_OPERATORS_MAP[query_item[0]]['name']
            converted_filters_list.append({key: convert_filter_list(query_item[1])})
    return converted_filters_list


## @brief converts a Lodel query filter into a MongoDB filter
# @param filter tuple : (FIELD, OPERATOR, VALUE) representing the query filter to convert
# @return dict : {KEY: {OPERATOR:VALUE}}
# @todo Add an error management for the operator mismatch
# @todo Add the checks for the type of values authorized in certain mongodb operators, such "$in" for example which takes a list
def convert_filter(filter):
    key, operator, value = filter
    converted_operator = LODEL_OPERATORS_MAP[operator]['name']
    converted_filter = {key: {converted_operator: value}}
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