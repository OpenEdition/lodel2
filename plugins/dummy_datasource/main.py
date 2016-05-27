#-*- coding:utf-8 -*-

class DummyDatasource(object):
    
    def __init__(self, *conn_args, **conn_kwargs):
        self.conn_args = conn_args
        self.conn_kwargs = conn_kwargs

    ## @brief returns a selection of documents from the datasource
    # @param target_cls Emclass
    # @param field_list list
    # @param filters list : List of filters
    # @param rel_filters list : List of relational filters
    # @param order list : List of column to order. ex: order = [('title', 'ASC'),]
    # @param group list : List of tupple representing the column to group together. ex: group = [('title', 'ASC'),]
    # @param limit int : Number of records to be returned
    # @param offset int: used with limit to choose the start record
    # @param instanciate bool : If true, the records are returned as instances, else they are returned as dict
    # @return list
    def select(self, target_cls, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0,
               instanciate=True):
        pass

    ## @brief Deletes one record defined by its uid
    # @param target_cls Emclass : class of the record to delete
    # @param uid dict|list : a dictionary of fields and values composing the unique identifier of the record or a list of several dictionaries
    # @return int : number of deleted records
    def delete(self, target_cls, uid):
        pass

    ## @brief updates one or a list of records
    # @param target_cls Emclass : class of the object to insert
    # @param uids list : list of uids to update
    # @param datas dict : datas to update (new values)
    # @return int : Number of updated records
    def update(self, target_cls, uids, **datas):
        pass

    ## @brief Inserts a record in a given collection
    # @param target_cls Emclass : class of the object to insert
    # @param datas dict : datas to insert
    # @return bool
    def insert(self, target_cls, **datas):
        pass

    ## @brief Inserts a list of records in a given collection
    # @param target_cls Emclass : class of the objects inserted
    # @param datas_list
    # @return list : list of the inserted records' ids
    def insert_multi(self, target_cls, datas_list):
        pass
