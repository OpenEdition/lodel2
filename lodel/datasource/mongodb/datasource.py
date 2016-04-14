# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import urllib

import lodel.datasource.mongodb.utils as utils


class MongoDbDataSourceError(Exception):
    pass


class MongoDbDataSource(object):

    MANDATORY_CONNECTION_ARGS = ('host', 'port', 'login', 'password', 'dbname')

    ## @brief Instanciates a Database object given a connection name
    # @param connection_name str
    def __init__(self, connection_name='default'):
        connection_args = self._get_connection_args(connection_name)
        login, password, host, port, dbname = MongoDbDataSource._check_connection_args(connection_args)

        # Creating of the connection
        connection_string = 'mongodb://%s:%s@%s:%s' % (login, password, host, port)
        self.connection = MongoClient(connection_string)
        # Getting the database
        self.database = self.connection[dbname]

    ## @brief Gets the settings given a connection name
    # @param connection_name str
    # @return dict
    # @TODO Change the return value using the Lodel 2 settings module
    def _get_connection_args(self, connection_name):
        return {
            'host': 'localhost',
            'port': 27017,
            'login': 'login',  # TODO modifier la valeur
            'password': 'password',  # TODO modifier la valeur
            'dbname': 'lodel'
        }

    ## @brief checks if the connection args are valid and complete
    # @param connection_args dict
    # @return bool
    # @todo checks on the argument types can be added here
    @classmethod
    def _check_connection_args(cls, connection_args):
        errors = []
        for connection_arg in cls.MANDATORY_CONNECTION_ARGS:
            if connection_arg not in connection_args:
                errors.append("Datasource connection error : %s parameter is missing." % connection_arg)
        if len(errors) > 0 :
            raise MongoDbDataSourceError("\r\n-".join(errors))

        return (connection_args['login'], urllib.quote_plus(connection_args['password']), connection_args['host'],
                connection_args['port'], connection_args['dbname'])


    ## @brief returns a selection of documents from the datasource
    # @param target_cls Emclass
    # @param field_list list
    def select(self, target_cls, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0,
               instanciate=True):
        collection_name = utils.object_collection_name(target_cls.__class__)
        collection = self.database[collection_name]
        query_filters = utils.parse_query_filters(filters)
        query_result_ordering = utils.parse_query_order(order) if order is not None else None
        results_field_list = None if len(field_list) == 0 else field_list  # TODO On peut peut-être utiliser None dans les arguments au lieu d'une liste vide
        limit = limit if limit is not None else 0
        cursor = collection.find(
            filter=query_filters,
            projection=results_field_list,
            skip=offset,
            limit=limit,
            sort=query_result_ordering
        )
        results = list()
        for document in cursor:
            results.append(document)

        return results

    ## @brief Deletes one record defined by its uid
    # @param target_cls Emclass : class of the record to delete
    # @param uid dict|list : a dictionary of fields and values composing the unique identifier of the record or a list of several dictionaries
    # @return int : number of deleted records
    # @TODO check the content of the result.raw_result property depending on the informations to return
    # @TODO Implement the error management
    def delete(self, target_cls, uid):
        if isinstance(uid, dict):
            uid = [uid]
        collection_name = utils.object_collection_name(target_cls.__class__)
        collection = self.database[collection_name]
        result = collection.delete_many(uid)
        return result.deleted_count

    def update(self, target_cls, uid, **datas):

        pass

    ## @brief Inserts a record in a given collection
    # @param target_cls Emclass : class of the object to insert
    # @param datas dict : datas to insert
    # @return bool
    # @TODO Implement the error management
    def insert(self, target_cls, **datas):
        collection_name = utils.object_collection_name(target_cls.__class__)
        collection = self.database[collection_name]
        result = collection.insert_one(datas)
        return len(result.inserted_id)

    ## @brief Inserts a list of records in a given collection
    # @param target_cls Emclass : class of the objects inserted
    # @param datas_list
    # @return list : list of the inserted records' ids
    # @TODO Implement the error management
    def insert_multi(self, target_cls, datas_list):
        collection_name = utils.object_collection_name(target_cls.__class__)
        collection = self.database[collection_name]
        result = collection.insert_many(datas_list)
        return len(result.inserted_ids)
