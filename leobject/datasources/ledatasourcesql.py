#-*- coding: utf-8 -*-

from ledatasource import LeDataSource

## SQL DataSource for LeObject
class LeDataSourceSQL(LeDataSource):

    def __init__(self, options=None):
        self.options = options

    ## @brief search for a collection of objects
    # @param emclass
    # @param emtype
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters
    def get(self, emclass, emtype, field_list, filters, relational_filters):
        pass
