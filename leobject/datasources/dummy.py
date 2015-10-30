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
        print ("DummyDatasource.update: ", letype, leclass, filters, rel_filters, data)
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
        print("DummyDatasource.delete: ", letype, leclass, filters, relational_filters)
        return True

    ## @brief search for a collection of objects
    # @param leclass LeClass : LeClass instance
    # @param letype LeType : LeType instance
    # @param field_list list : list of fields to get from the datasource
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE) (see @ref leobject_filters )
    # @param relational_filters list : relationnal filters list (see @ref leobject_filters )
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, leclass, letype, field_list, filters, relational_filters):
        print("DummyDatasource.get: ", leclass, letype, field_list, filters, relational_filters)
        return []
    
    ## @brief Link two object given a relation nature, depth and rank
    # @param id_sup int : a lodel_id
    # @param id_sub int : a lodel_id
    # @param nature str|None : The relation nature or None if rel2type
    # @param rank int : a rank
    def add_relation(self, id_sup, id_sub, nature=None, depth=None, rank=None):
        pass

    ## @brief Delete a link between two objects given a relation nature
    # @param id_sup int : a lodel_id
    # @param id_sub int : a lodel_id
    # @param nature str|None : The relation nature
    def del_relation(self, id_sup, id_sub, nature=None):
        pass
    
    ## @brief Return all relation of a lodel_id given a position and a nature
    # @param lodel_id int : We want the relations of this lodel_id
    # @param superior bool : If true search the relations where lodel_id is in id_sup
    # @param nature str|None : Search for relations with the given nature (if None rel2type)
    # @param return an array of dict with keys [ id_sup, id_sub, rank, depth, nature ]
    def get_relations(self, lodel_id, superior=True, nature=None):
        pass
