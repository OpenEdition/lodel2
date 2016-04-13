# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import urllib

import lodel.datasource.mongodb.utils as utils
from lodel.settings.settings import Settings

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

    def select(self, target_cls, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0,
               instanciate=True):
        pass

    def delete(self, target_cls, uid):
        pass

    def update(self, target_cls, uid, **datas):
        pass

    ## @brief Inserts a record in a given collection
    # @param target_cls Emclass : class of the object to insert
    # @param datas dict : datas to insert
    # @return ObjectId : the uid of the inserted record
    def insert(self, target_cls, **datas):
        collection_name = utils.object_collection_name(target_cls.__class__)
        collection = self.database[collection_name]
        result = collection.insert_one(datas)
        return result.inserted_id

    ## @brief Inserts a list of records in a given collection
    # @param target_cls Emclass : class of the objects inserted
    # @param datas_list
    # @return int : Number of inserted records in the collection
    def insert_multi(self, target_cls, datas_list):
        collection_name = utils.object_collection_name(target_cls.__class__)
        collection = self.database[collection_name]
        bulk = collection.initialize_ordered_bulk_op()
        for datas_list_item in datas_list:
            bulk.insert(datas_list_item)
        try:
            result = bulk.execute()
        except BulkWriteError as bwe:
            pass  # TODO add the behavior in case of an exception => bwe.details['writeErrors'], is a list of error info dicts

        return result['nInserted']
