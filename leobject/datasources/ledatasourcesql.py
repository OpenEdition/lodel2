#-*- coding: utf-8 -*-

import pymysql

from leobject.datasources.dummy import DummyDatasource
from leobject.leobject import REL_SUB, REL_SUP

from mosql.db import Database, all_to_dicts
from mosql.query import select, insert, update, delete, join
from mosql.util import raw
import mosql.mysql

## MySQL DataSource for LeObject
class LeDataSourceSQL(DummyDatasource):

    RELATIONS_TABLE_NAME = 'relations'
    RELATIONS_POSITIONS_FIELDS = { REL_SUP: 'superior_id', REL_SUB: 'subordinate_id'}
    RELATIONS_NATURE_FIELD = 'nature'
    LODEL_ID_FIELD = 'lodel_id'
    CLASS_TABLE_PREFIX = 'class_'
    OBJECTS_TABLE_NAME = 'object'

    def __init__(self, module=pymysql, conn_args={'host': '127.0.0.1', 'user':'lodel', 'passwd':'bruno', 'db': 'lodel2'}):
        super(LeDataSourceSQL, self).__init__()
        self.module = module
        self.connection = Database(pymysql, host=conn_args['host'], user=conn_args['user'], passwd=conn_args['passwd'], db=conn_args['db'])

    ## @brief inserts a new object
    # @param letype LeType
    # @param leclass LeClass
    # @param datas dict : dictionnary of field:value pairs to save
    # @return int : lodel_id of the created object
    # @todo add the returning clause and the insertion in "object"
    def insert(self, letype, leclass, datas):
        query_table_name = self._get_table_name_from_class_name(leclass.__name__)

        query = insert(query_table_name, datas)
        with self.connection as cur:
            cur.execute(query)

        return True

    ## @brief search for a collection of objects
    # @param leclass LeClass
    # @param letype LeType
    # @field_list list
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relation_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return list
    def get(self, leclass, letype, field_list, filters, relational_filters=None):

        query_table_name = self._get_table_name_from_class_name(leclass.__name__)
        where_filters = self._prepare_filters(filters, query_table_name)
        join_fields = {}

        if relational_filters is not None and len(relational_filters) > 0:
            rel_filters = self._prepare_rel_filters(relational_filters)
            for rel_filter in rel_filters:
                # join condition
                relation_table_join_field = "%s.%s" % (self.RELATIONS_TABLE_NAME, self.RELATIONS_POSITIONS_FIELDS[rel_filter['position']])
                query_table_join_field = "%s.%s" % (query_table_name, self.LODEL_ID_FIELD)
                join_fields[query_table_join_field] = relation_table_join_field
                # Adding "where" filters
                where_filters['%s.%s' % (self.RELATIONS_TABLE_NAME, self.RELATIONS_NATURE_FIELD)] = rel_filter['nature']
                where_filters[rel_filter['condition_key']] = rel_filter['condition_value']

            # building the query
            query = select(query_table_name, where=where_filters, select=field_list, joins=join(self.RELATIONS_TABLE_NAME, join_fields))
        else:
            query = select(query_table_name, where=where_filters, select=field_list)

        # Executing the query
        with self.connection as cur:
            results = all_to_dicts(cur.execute(query))

        return results

    ## @brief delete an existing object
    # @param letype LeType
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return bool : True on success
    def delete(self, letype, leclass, filters, relational_filters):
        query_table_name = self._get_table_name_from_class_name(leclass.__name__)
        prep_filters = self._prepare_filters(filters, query_table_name)
        prep_rel_filters = self._prepare_rel_filters(relational_filters)

        if len(prep_rel_filters) > 0:
            query = "DELETE %s FROM " % query_table_name

            for prep_rel_filter in prep_rel_filters:
                query += "%s INNER JOIN %s ON (%s.%s = %s.%s)" % (
                    self.RELATIONS_TABLE_NAME,
                    query_table_name,
                    self.RELATIONS_TABLE_NAME,
                    prep_rel_filter['position'],
                    query_table_name,
                    self.LODEL_ID_FIELD
                )

                if prep_rel_filter['condition_key'][0] is not None:
                    prep_filters[("%s.%s" % (self.RELATIONS_TABLE_NAME, prep_rel_filter['condition_key'][0]), prep_rel_filter['condition_key'][1])] = prep_rel_filter['condition_value']

        if prep_filters is not None and len(prep_filters) > 0:
            query += " WHERE "
            filter_counter = 0
            for filter_item in prep_filters:
                if filter_counter > 1:
                    query += " AND "
                query += "%s %s %s" % (filter_item[0][0], filter_item[0][1], filter_item[1])
        else:
            query = delete(query_table_name, filters)

        with self.connection as cur:
            cur.execute(query)

        return True

    ## @brief update an existing object's data
    # @param letype LeType
    # @param leclass LeClass
    # @param  filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param rel_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @param data dict
    # @return bool
    # @todo prendre en compte les rel_filters
    def update(self, letype, leclass, filters, rel_filters, data):

        query_table_name = self._get_table_name_from_class_name(leclass.__name__)
        where_filters = filters
        set_data = data

        prepared_rel_filters = self._prepare_rel_filters(rel_filters)

        # Building the query
        query = update(table=query_table_name, where=where_filters, set=set_data)
        # Executing the query
        with self.connection as cur:
            cur.execute(query)
        return True


    ## @brief prepares the table name using a "class_" prefix
    # @params classname str
    # @return str
    def _get_table_name_from_class_name(self, classname):
        return classname if self.CLASS_TABLE_PREFIX in classname else "%s%s" % (self.CLASS_TABLE_PREFIX, classname)

    ## @brief prepares the relational filters
    # @params rel_filters : (("superior"|"subordinate"), operator, value)
    # @return list
    def _prepare_rel_filters(self, rel_filters):
        prepared_rel_filters = []

        if rel_filters is not None and len(rel_filters) > 0:
            for rel_filter in rel_filters:
                rel_filter_dict = {
                    'position': REL_SUB if rel_filter[0][0] == REL_SUP else REL_SUB,
                    'nature': rel_filter[0][1],
                    'condition_key': (self.RELATIONS_POSITIONS_FIELDS[rel_filter[0][0]], rel_filter[1]),
                    'condition_value': rel_filter[2]
                }
                prepared_rel_filters.append(rel_filter_dict)

        return prepared_rel_filters

    ## @brief prepares the filters to be used by the mosql library's functions
    # @params filters : (FIELD, OPERATOR, VALUE) tuples
    # @return dict : Dictionnary with (FIELD, OPERATOR):VALUE style elements
    def _prepare_filters(self, filters, tablename=None):
        prepared_filters = {}
        if filters is not None and len(filters) > 0:
            for filter_item in filters:
                if '.' in filter_item[0]:
                    prepared_filter_key = (filter_item[0], filter_item[1])
                else:
                    prepared_filter_key = ("%s.%s" % (tablename, filter_item[0]), filter_item[1])
                prepared_filter_value = filter_item[2]
                prepared_filters[prepared_filter_key] = prepared_filter_value

        return prepared_filters