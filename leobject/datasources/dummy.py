#-*- coding: utf-8 -*-


## dummy datasource for LeObject
# This class has to be extended to apply to a real datasource
# But it can be used as an empty and debug datasource

class DummyDatasource(object):

    def __init__(self, module=None, *conn_args, **conn_kargs):
        self.module = module
        self.conn_args = conn_args
        self.conn_kargs = conn_kargs

    ## @brief update an existing LeObject
    # @param lodel_id (int) : list of lodel_id
    # @param checked_data dict
    # @param filters
    # @param relational_filters
    def update(self, lodel_id, checked_data, filters, relational_filters):
        print ("DummyDatasource.update: ", lodel_id, checked_data, filters, relational_filters)
        return True

    ## @brief create a new LeObject
    # @param letype LeType
    # @param leclass LeClass
    # @param data dict: a dictionnary of field:value to save
    # @return lodel_id int: new lodel_id of the newly created LeObject
    def insert(self, letype, leclass, **datas):
        print("DummyDatasource.insert: ", letype, leclass, datas)
        return 42

    ## @brief delete an existing LeObject
    # @param lodel_id int | (int): lodel_id of the object(s) to delete
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list
    # @return okay bool: True on success, it will raise on failure
    def delete(self, lodel_id, filters, relational_filters):
        print("DummyDatasource.delete: ", lodel_id)
        return True

    ## @brief search for a collection of objects
    # @param emclass LeClass : LeClass instance
    # @param emtype LeType : LeType instance
    # @param field_list list : list of fields to get from the datasource
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, emclass, emtype, field_list, filters, relational_filters):
        print("DummyDatasource.get: ", emclass, emtype, field_list, filters, relational_filters)
        return []
