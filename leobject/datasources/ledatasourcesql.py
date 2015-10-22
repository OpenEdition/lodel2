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

    def _prepare_filters(self, filters):
        prepared_filters = {}
        for filter in filters:
            prepared_filter_key = (filter[0], filter[1])
            prepared_filter_value = filter[2]
            prepared_filters[prepared_filter_key] = prepared_filter_value

        return prepared_filters