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


class MongoDbDataSourceError(Exception):
    pass


class MongoDbDataSource(object):

    MANDATORY_CONNECTION_ARGS = ('host', 'post', 'login', 'password', 'dbname')

    def __init__(self, module=pymongo, connection_args=DEFAULT_CONNECTION):
        login, password, host, port, dbname = MongoDbDataSource._check_connection_args(connection_args)

        # Creating of the connection
        connection_string = 'mongodb://%s:%s@%s:%s' % (login, password, host, port)
        self.connection = MongoClient(connection_string)
        # Getting the database
        self.database = self.connection[dbname]

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

    def select(self, target_cls, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0, instanciate=True):
        pass

    def delete(self, target_cls, uid):
        pass

    def update(self, target_cls, uid, **datas):
        pass

    def insert(self, target_cls, **datas):
        pass

    def insert_multi(self, target_cls, datas_list):
        pass
