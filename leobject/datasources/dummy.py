#-*- coding: utf-8 -*-

## @brief Dummy datasource for LeObject
#
# This class has to be extended to apply to a real datasource
# But it can be used as an empty and debug datasource
class DummyDatasource(object):

    def __init__(self, module=None, *conn_args, **conn_kargs):
        self.module = module
        self.conn_args = conn_args
        self.conn_kargs = conn_kargs

    ## @brief update an existing LeObject
    # @param letype LeType : LeType child class
    # @param leclass LeClass : LeClass child class
    # @param filters list : List of filters (see @ref leobject_filters )
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters )
    # @param data dict : Dict representing fields and there values
    # @return True if success
    def update(self, letype, leclass, filters, rel_filters, data):
        print ("DummyDatasource.update: ", lodel_id, checked_data, filters, relational_filters)
        return True

    ## @brief create a new LeObject
    # @param letype LeType : LeType child class
    # @param leclass LeClass : LeClass child class
    # @param data list: a lis of dictionnary of field:value to save
    # @return lodel_id int: new lodel_id of the newly created LeObject
    def insert(self, letype, leclass, datas):
        print("DummyDatasource.insert: ", letype, leclass, datas)
        return 42

    ## @brief delete an existing LeObject
    # @param letype LeType : LeType child class
    # @param leclass LeClass : LeClass child class
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE) (see @ref leobject_filters )
    # @param relational_filters list : relationnal filters list (see @ref leobject_filters )
    # @return okay bool: True on success, it will raise on failure
    def delete(self, letype, leclass, filters, relational_filters):
        print("DummyDatasource.delete: ", lodel_id)
        return True

    ## @brief search for a collection of objects
    # @param leclass LeClass : LeClass instance
    # @param letype LeType : LeType instance
    # @param field_list list : list of fields to get from the datasource
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE) (see @ref leobject_filters )
    # @param relational_filters list : relationnal filters list (see @ref leobject_filters )
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, leclass, letype, field_list, filters, relational_filters):
        print("DummyDatasource.get: ", emclass, emtype, field_list, filters, relational_filters)
        return []
