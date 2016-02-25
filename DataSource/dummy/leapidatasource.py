#-*- coding: utf-8 -*-

## @brief Dummy datasource for LeObject
#
# This class has to be extended to apply to a real datasource
# But it can be used as an empty and debug datasource
#
# @todo Settings fetch/pass generalisation for datasources.
class LeapiDataSource(object):
    
    ## @todo Settings fetch/pass generalisation for datasources.
    def __init__(self, module=None, *conn_args, **conn_kargs):
        self.module = module
        self.conn_args = conn_args
        self.conn_kargs = conn_kargs

    ## @brief select lodel editorial components given filters
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param field_list list : List of field names we want in the returned value or instance
    # @param filters list : List of filters (see @ref leobject_filters )
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters )
    # @param group list of tupple: List of column to group together.  group = [('titre', 'ASC'), ]
    # @param order list of tupple : List of column to order.  order = [('titre', 'ASC'), ]
    # @param limit int : Number of row to be returned
    # @param offset int : Used with limit to choose the start row
    # @param instanciate bool : If True return an instance, else return a dict
    # @return a list of LeCrud child classes
    def select(self, target_cls, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0, instanciate=True):
        pass

    ## @brief delete lodel editorial components given filters
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param leo_id int : The component ID (lodel_id or relation_id)
    # @return the number of deleted components
    def delete(self, target_cls, leo_id):
        pass

    ## @brief update an existing lodel editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param leo_id int : The uniq ID of the object we want to update
    # @param **datas : Datas in kwargs
    # @return The number of updated components
    def update(self, target_cls, leo_id, **datas):
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
