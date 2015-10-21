#-*- coding: utf-8 -*-

## Generic DataSource for LeObject

class LeDataSource(object):

    def __init__(self, module=None, *conn_args, **conn_kargs):
        self.module = module
        self.conn_args = conn_args
        self.conn_kargs = conn_kargs

    ## @brief update an existing LeObject
    # @param lodel_id (int) : list of lodel_id
    # @param checked_data dict
    # @param datasource_filters (string)
    def update(self, lodel_id, checked_data, datasource_filters):
        return True

    ## @brief insert
    # @param typename string
    # @param classname string
    # @param **datas dict
    def insert(self, typename, classname, **datas):
        return True

    ## @brief delete
    # @param lodel_id (int) : list of lode_id(s) to delete
    def delete(self, lodel_id):
        return True
    
    ## @brief search for a collection of objects
    # @param emclass LeClass : LeClass instance
    # @param emtype LeType : LeType instance
    # @param field_list list : list of fields to get from the datasource
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters
    def get(self, emclass, emtype, field_list, filters, relational_filters):
        return {}

