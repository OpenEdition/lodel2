#-*- coding: utf-8 -*-

## Generic DataSource for LeObject

class LeDataSource(object):

    def __init__(self, options=None):
        self.options = options


    ## @brief search for a collection of objects
    # @param emclass LeClass : LeClass instance
    # @param emtype LeType : LeType instance
    # @param field_list list : list of fields to get from the datasource
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters
    def get(self, emclass, emtype, field_list, filters, relational_filters):
        return False

