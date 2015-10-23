#-*- coding: utf-8 -*-

from leobject.datasources.dummy import DummyDatasource
from mosql.db import Database, all_to_dicts
from mosql.query import select

from Lodel.utils.mosql import *

## SQL DataSource for LeObject
class LeDataSourceSQL(DummyDatasource):

    def __init__(self, module=None, *conn_args, **conn_kargs):
        super(LeDataSourceSQL, self).__init__()
        self.db = Database(self.module, self.conn_args, self.conn_kargs)

    ## @brief update an existing object's data
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param data dict
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @param letype LeType
    # @return bool
    def update (self, leclass, filters, data, relational_filters=None, letype=None):
        pass

    ## @brief create a new object in the datasource
    # @param leclass LeClass
    # @param letype LeType
    # @param datas dict : dictionnary of field:value pairs to save
    # @return int : lodel_id of the created object
    def insert(self, leclass, letype=None, **datas):
        pass

    ## @brief delete an existing object
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @param letype LeType
    # @return bool : True on success
    def delete(self, leclass, filters, relational_filters=None, letype=None):
        pass

    ## @brief search for a collection of objects
    # @param emclass LeClass
    # @param emtype LeType
    # @field_list list
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    def get(self, emclass, emtype, field_list, filters, relational_filters=None):

        tablename = emclass.name
        where_filters = self._prepare_filters(filters)
        if relational_filters or len(relational_filters) > 0:
            for relational_filter in relational_filters:
                relational_position = relational_filter[0][0]
                relational_field = relational_filter[0][1]
                relational_operator = relational_filter[1]
                relational_value = relational_filter[2]



        tablename =  emclass.name
        where_filters = self._prepare_filters(filters)
        if relational_filters or len(relational_filters) > 0:
            rel_filters = self._prepare_filters(relational_filters)
            query = select(tablename, where=where_filters, select=field_list, joins=join('relations', {}))
        else:
            query = select(tablename, where=where_filters, select=field_list)
        self.db.execute(query)

        return all_to_dicts(self.db)

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