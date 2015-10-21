#-*- coding: utf-8 -*-

## Generic DataSource for LeObject

class LeDataSource(object):

    def __init__(self, options=None):
        self.options = options


    ## @brief search for a collection of objects
    # @param emclass
    # @param emtype
    # @param filters
    # @param relational_filters
    def get(self, emclass, emtype, filters, relational_filters):
        pass

