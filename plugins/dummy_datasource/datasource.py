#-*- coding:utf-8 -*-

class DummyDatasource(object):
    
    def __init__(self, *conn_args, **conn_kwargs):
        self.conn_args = conn_args
        self.conn_kwargs = conn_kwargs
    
    ##@brief Provide a new uniq numeric ID
    #@param emcomp LeObject subclass (not instance) : To know on wich things we
    #have to be uniq
    #@return an integer
    def new_numeric_id(self, emcomp):
        pass

    ##@brief returns a selection of documents from the datasource
    #@param target_cls Emclass
    #@param field_list list
    #@param filters list : List of filters
    #@param rel_filters list : List of relational filters
    #@param order list : List of column to order. ex: order = [('title', 'ASC'),]
    #@param group list : List of tupple representing the column to group together. ex: group = [('title', 'ASC'),]
    #@param limit int : Number of records to be returned
    #@param offset int: used with limit to choose the start record
    #@param instanciate bool : If true, the records are returned as instances, else they are returned as dict
    #@return list
    def select(self, target_cls, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0,
               instanciate=True):
        pass

    ##@brief Deletes records according to given filters
    #@param target Emclass : class of the record to delete
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@return int : number of deleted records
    def delete(self, target, filters, relational_filters):
        return 0

    ## @brief updates records according to given filters
    #@param target Emclass : class of the object to insert
    #@param filters list : List of filters
    #@param rel_filters list : List of relational filters
    #@param upd_datas dict : datas to update (new values)
    #@return int : Number of updated records
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
