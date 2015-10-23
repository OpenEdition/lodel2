#-*- coding: utf-8 -*-

import sqlite3
from leobject.datasources.dummy import DummyDatasource
from mosql.db import Database, all_to_dicts
from mosql.query import select, insert
from leobject import REL_SUB, REL_SUP

from Lodel.utils.mosql import *

## SQL DataSource for LeObject
class LeDataSourceSQL(DummyDatasource):

    RELATIONS_TABLE_NAME = 'relations'
    RELATIONS_POSITIONS_FIELDS = {REL_SUP:'superior_id', REL_SUB:'subordinate_id'}
    MODULE = 'sqlite3'

    def __init__(self, module=None, *conn_args, **conn_kargs):
        self.module = self.MODULE if module == None else module
        super(LeDataSourceSQL, self).__init__()
        self.db = Database(self.module, self.conn_args, self.conn_kargs)

    ## @brief update an existing object's data
    # @param letype LeType
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param rel_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @param data dict
    # @return bool
    def update(self, letype, leclass, filters, rel_filters, data):
        pass

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
        with self.db as cur:
            cur.execute(query)
        return True

    ## @brief delete an existing object
    # @param letype LeType
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return bool : True on success
    def delete(self, letype, leclass, filters, relational_filters):
        pass

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

        if relational_filters or len(relational_filters) > 0:
            for relational_filter in relational_filters:
                # Parsing the relation_filter
                relational_position = relational_filter[0][0]
                relational_field = relational_filter[0][1]
                relational_operator = relational_filter[1]
                relational_value = relational_filter[2]
                relational_where_filters_key = (relational_field, relational_operator)
                relational_where_filters_value = relational_value

                # Definition of the join condition
                relation_table_join_field = "%s.%s" % (self.RELATIONS_TABLE_NAME, self.RELATIONS_POSITIONS_FIELDS[relational_position])
                query_table_join_field = "%s.lodel_id" % query_table_name
                join_fields[query_table_join_field] = relation_table_join_field

                # Adding "where" filters
                where_filters[relational_where_filters_key] = relational_where_filters_value

            # Building the query
            query = select(query_table_name, where=where_filters, select=field_list, joins=join(self.RELATIONS_TABLE_NAME, join_fields))
        else:
            query = select(query_table_name, where=where_filters, select=field_list)

        # Executing the query
        with self.db as cur:
            results = cur.execute(query)

        # Returning it as a list of dict
        return all_to_dicts(results)

    # @brief prepares the filters to be used by the mosql library's functions
    # @params filters : (FIELD, OPERATOR, VALUE) tuples
    # @return dict : Dictionnary with (FIELD, OPERATOR):VALUE style elements
    def _prepare_filters(self, filters):
        prepared_filters = {}
        for filter in filters:
            prepared_filter_key = (filter[0], filter[1])
            prepared_filter_value = filter[2]
            prepared_filters[prepared_filter_key] = prepared_filter_value

        return prepared_filters