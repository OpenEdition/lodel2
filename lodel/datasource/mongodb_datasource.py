# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient


DEFAULT_CONNECTION = {
    'host': 'localhost',
    'port': 27017,
    'dbname': 'lodel'
}

class MongoDbDataSource(object):

    def __init__(self, module=pymongo, connection_args=DEFAULT_CONNECTION):
        self.connection = MongoClient(connection_args['host'], connection_args['port'])
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
