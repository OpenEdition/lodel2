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
    # @param lodel_id int : lodel_id of the object to update
    # @param checked_data dict
    # @param filters
    # @param relational_filters
    def update (self, lodel_id, checked_data, filters, relational_filters):
        pass

    ## @brief create a new object in the datasource
    # @param letype LeType
    # @param leclass LeClass
    # @param data dict : dictionnary of field:value pairs to save
    # @return lodel_id int : lodel_id of the created object
    def insert(self, letype, leclass, **data):
        pass

    ## @brief delete an existing object
    # @param lodel_id int : lodel_id of the object to delete
    # @param filters list : list of typles formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list
    # @return bool : True on success
    def delete(self, lodel_id, filters, relational_filters):
        pass

    ## @brief search for a collection of objects
    # @param emclass
    # @param emtype
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters
    def get(self, emclass, emtype, field_list, filters, relational_filters):

        tablename =  emclass.name
        where_filters = self._prepare_filters(filters)
        rel_filters = self._prepare_filters(relational_filters)
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