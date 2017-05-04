#-*- coding:utf-8 -*-

## @package lodel.plugins.dummy_datasource.datasource This module contains the main class of the datasource, implementing the basic operations one can perform.

from lodel.plugin.datasource_plugin import AbstractDatasource

## @brief Datasource class, inherited from @ref lodel.plugin.datasource.AbstractDatasource
class DummyDatasource(AbstractDatasource):
    
    ##
    # @param conn_args list
    # @param conn_kwargs dict
    def __init__(self, *conn_args, **conn_kwargs):
        self.conn_args = conn_args
        self.conn_kwargs = conn_kwargs
    
    ## @brief Provides a new unique numeric ID
    # @param emcomp LeObject subclass (not instance) : The class against whom we have to be unique
    # @return an integer
    def new_numeric_id(self, emcomp):
        pass

    ## @brief returns a selection of documents from the datasource
    # @param target Emclass
    # @param field_list list
    # @param filters list : List of filters
    # @param relational_filters list : List of relational filters (default value : None)
    # @param order list : List of column to order. ex: order = [('title', 'ASC'),] (default value : None)
    # @param group list : List of tupple representing the column to group together. ex: group = [('title', 'ASC'),] (default value : None)
    # @param limit int : Number of records to be returned (default value : None)
    # @param offset int: used with limit to choose the start record (default value : 0)
    # @param instanciate bool : If true, the records are returned as instances, else they are returned as dict (default value : True)
    # @return list
    def select(self, target, field_list, filters, relational_filters=None, order=None, group=None, limit=None, offset=0,
               instanciate=True):
        pass

    ## @brief Deletes records according to given filters
    # @param target Emclass : class of the record to delete
    # @param filters list : List of filters
    # @param relational_filters list : List of relational filters
    # @return int : number of deleted records
    def delete(self, target, filters, relational_filters):
        return 0

    ## @brief updates records according to given filters
    # @param target Emclass : class of the object to insert
    # @param filters list : List of filters
    # @param relational_filters list : List of relational filters
    # @param upd_datas dict : datas to update (new values)
    # @return int : Number of updated records
    def update(self, target, filters, relational_filters, upd_datas):
        return 0

    ## @brief Inserts a record in a given collection
    # @param target Emclass : class of the object to insert
    # @param new_datas dict : datas to insert
    # @return the inserted uid
    def insert(self, target, new_datas):
        return 0

    ## @brief Inserts a list of records in a given collection
    # @param target Emclass : class of the objects inserted
    # @param datas_list list : list of dict
    # @return list : list of the inserted records' ids
    def insert_multi(self, target, datas_list):
        return 0
