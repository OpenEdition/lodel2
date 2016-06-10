# -*- coding: utf-8 -*-
import unittest
from pymongo import MongoClient
from plugins.mongodb_datasource.migration_handler import *

class MongoDbMigrationHandlerTestCase(unittest.TestCase):

    def test_check_connection_args(self):
        empty_connection_args = {}
        with self.assertRaises(MigrationHandlerError):
            MongoDbMigrationHandler(empty_connection_args)

        bad_connection_args_dicts = [
            {'host': 'localhost', 'port': 20030},
            {'host': 'localhost', 'port': 28015},
            {'host': 'localhost', 'port': 28015, 'login':'lodel', 'password': 'lap'}
        ]
        for bad_connection_args_dict in bad_connection_args_dicts:
            with self.assertRaises(MigrationHandlerError):
                MongoDbMigrationHandler(bad_connection_args_dict)

    def test_init_db(self):
        correct_connection_args = {'host': 'localhost', 'port': 28015, 'username': 'lodel_admin', 'password': 'lapwd', 'db_name': 'lodel'}
        migration_handler = MongoDbMigrationHandler(correct_connection_args)
        migration_handler._install_collections()
