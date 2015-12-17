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
    
    ## @brief select lodel editorial components given filters
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param filters list : List of filters (see @ref leobject_filters )
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters )
    # @return a list of LeCrud child classes
    def select(self, target_cls, field_list, filters, rel_filters):
        pass

    ## @brief delete lodel editorial components given filters
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param filters list : List of filters (see @ref leobject_filters )
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters )
    # @return the number of deleted components
    def delete(self, target_cls, filters, rel_filters):
        pass

    ## @brief update an existing lodel editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param filters list : List of filters (see @ref leobject_filters )
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters )
    # @param **datas : Datas in kwargs
    # @return The number of updated components
    def update(self, target_cls, filters, rel_filters, **datas):
        pass
    
    ## @brief insert a new lodel editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param **datas : The datas to insert
    # @return The inserted component's id
    def insert(self, target_cls, **datas):
        pass
    
    ## @brief insert multiple editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param datas_list list : A list of dict representing the datas to insert
    # @return int the number of inserted component
    def insert_multi(self, target_cls, datas_list):
        pass
    
    ## @brief Update a rank for a relation (and shift properly every concerned relations)
    # @param le_relation LeRelation : A LeRelation instance
    # @param new_rank int : An integer representing the absolute new rank
    # @return ???
    def update_rank(self, le_relation, new_rank):
        pass
