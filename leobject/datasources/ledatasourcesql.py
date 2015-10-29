#-*- coding: utf-8 -*-

import sqlite3
from leobject.datasources.dummy import DummyDatasource
from mosql.db import Database, all_to_dicts
from mosql.query import select, insert, update, delete, join
from leobject.leobject import REL_SUB, REL_SUP

## SQL DataSource for LeObject
class LeDataSourceSQL(DummyDatasource):

    RELATIONS_TABLE_NAME = 'relations'
    RELATIONS_POSITIONS_FIELDS = {REL_SUP: 'superior_id', REL_SUB: 'subordinate_id'}
    RELATIONS_NATURE_FIELD = 'nature'

    MODULE = sqlite3

    def __init__(self, module=None, *conn_args, **conn_kargs):
        super(LeDataSourceSQL, self).__init__()
        self.module = self.MODULE if module is None else module
        self.connection = Database(self.module, *conn_args, **conn_kargs)

    ## @brief update an existing object's data
    # @param letype LeType
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param rel_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @param data dict
    # @return bool
    # @todo prendre en compte les rel_filters
    def update(self, letype, leclass, filters, rel_filters, data):

        query_table_name = leclass.name
        where_filters = filters
        set_data = data

        # Building the query
        query = update(table=query_table_name, where=where_filters, set=set_data)
        # Executing the query
        with self.connection as cur:
            cur.execute(query)
        return True

    ## @brief create a new object in the datasource
    # @param letype LeType
    # @param leclass LeClass
    # @param datas dict : dictionnary of field:value pairs to save
    # @return int : lodel_id of the created object
    def insert(self, letype, leclass, datas):
        query_table_name = leclass.name
        #building the query
        query = insert(query_table_name, datas)
        #executing the query
        with self.connection as cur:
            cur.execute(query)
        return True

    ## @brief delete an existing object
    # @param letype LeType
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return bool : True on success
    # @todo prendre en compte les rel_filters
    def delete(self, letype, leclass, filters, relational_filters):
        query_table_name = leclass.name
        query = delete(query_table_name, filters)
        with self.connection as cur:
            cur.execute(query)
        return True

    ## @brief search for a collection of objects
    # @param leclass LeClass
    # @param letype LeType
    # @field_list list
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return list
    def get(self, leclass, letype, field_list, filters, relational_filters=None):

        query_table_name = leclass.name
        where_filters = self._prepare_filters(filters)
        join_fields = {}

        if relational_filters is not None and len(relational_filters) > 0:
            for relational_filter in relational_filters:
                # Parsing the relation_filter
                relational_position = REL_SUB if relational_filter[0][0] == REL_SUP else REL_SUP
                relational_nature = relational_filter[0][1]
                relational_operator = relational_filter[1]

                relational_condition_key = (self.RELATIONS_POSITIONS_FIELDS[relational_filter[0][0]], relational_operator)
                relational_condition_value = relational_filter[2]

                # Definition of the join condition
                relation_table_join_field = "%s.%s" % (self.RELATIONS_TABLE_NAME, self.RELATIONS_POSITIONS_FIELDS[relational_position])
                query_table_join_field = "%s.lodel_id" % query_table_name
                join_fields[query_table_join_field] = relation_table_join_field

                # Adding "where" filters
                where_filters['%s.%s' % (self.RELATIONS_TABLE_NAME, self.RELATIONS_NATURE_FIELD)] = relational_nature
                where_filters[relational_condition_key] = relational_condition_value

            # Building the query
            query = select(query_table_name, where=where_filters, select=field_list, joins=join(self.RELATIONS_TABLE_NAME, join_fields))
        else:
            query = select(query_table_name, where=where_filters, select=field_list)

        # Executing the query
        with self.db as cur:
            results = all_to_dicts(cur.execute(query))

        # Returning it as a list of dict
        return results

    ## @brief prepares the filters to be used by the mosql library's functions
    # @params filters : (FIELD, OPERATOR, VALUE) tuples
    # @return dict : Dictionnary with (FIELD, OPERATOR):VALUE style elements
    def _prepare_filters(self, filters):
        prepared_filters = {}
        for filter_item in filters:
            prepared_filter_key = (filter_item[0], filter_item[1])
            prepared_filter_value = filter_item[2]
            prepared_filters[prepared_filter_key] = prepared_filter_value

        return prepared_filters
