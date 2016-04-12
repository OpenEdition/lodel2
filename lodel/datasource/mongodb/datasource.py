# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

import urllib

# TODO Positionner cette variable dans les settings
DEFAULT_CONNECTION = {
    'host': 'localhost',
    'port': 27017,
    'login': 'login',  # TODO modifier la valeur
    'password': 'password',  # TODO modifier la valeur
    'dbname': 'lodel'
}

class MongoDbDataSource(object):

    def __init__(self, module=pymongo, connection_args=DEFAULT_CONNECTION):
        connection_string = 'mongodb://%s:%s@%s:%s' % (connection_args['login'],
                                                       urllib.quote_plus(connection_args['password']),
                                                       connection_args['host'],
                                                       connection_args['port'])
        self.connection = MongoClient(connection_string)
        self.database = self.connection[connection_args['dbname']]

    ##@brief Inserts a list of records in a given collection
    #
    # @param collection_name str : name of the MongoDB collection in which we will insert the records
    # @param datas list : list of dictionaries corresponding to the records
    # @throw BulkWriteError : is thrown when an error occurs during the execution of the ordered bulk operations
    def insert(self, collection_name, datas):
        collection = self.database[collection_name]
        bulk = collection.initialize_ordered_bulk_op()
        # TODO check if all the elements of the list are dictionaries
        bulk.insert_many(datas)
        try:
            result = bulk.execute()
        except BulkWriteError as bwe:
            pass  # TODO Add the behavior in case of an exception => bwe.details['writeErrors'], is a list of error info dicts

        return result['nInserted']

    def select(self):

        pass
    
    def update(self):
        pass

    def delete(self, target_cls, uid):
        uidname = target_cls.uidname
        collection_name = target_cls.collection_name
        result = self.database[collection_name].delete_many({uidname: uid})
        return result.deteled_count
