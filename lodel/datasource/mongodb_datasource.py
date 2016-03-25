# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
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

    def insert(self):
        pass

    def select(self):
        pass
    
    def update(self):
        pass

    def delete(self, target_cls, uid):
        uidname = target_cls.uidname
        collection_name = target_cls.collection_name
        result = self.database[collection_name].delete_many({uidname: uid})
        return result.deteled_count
