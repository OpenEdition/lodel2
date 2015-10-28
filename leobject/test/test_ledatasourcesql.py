# -*- coding: utf8 -*-

import unittest
import sqlite3
from unittest import TestCase
from leobject.datasources.ledatasourcesql import LeDataSourceSQL
from mosql.db import Database


class _LeDataSourceTestCase(TestCase):

    def setUp(self):
        self.mydatasource = LeDataSourceSQL(sqlite3, *{'db.sqlite3': '127.0.0.1'})

    def tearDown(self):
        del self.mydatasource

    def test_connection(self):
        """Tests if the connection occurs"""
        self.assertIsInstance(obj=self.mydatasource, cls=LeDataSourceSQL, msg='A %s object was expected, %s obtained instead' % (LeDataSourceSQL.__class__, self.mydatasource.__class__))
        self.assertIsNotNone(obj=self.mydatasource.connection, msg='The database connection cursor could not be instanciated')
        self.assertIsInstance(self.mydatasource.connection, Database, msg='%s object was expected for the connection cursor, %s obtained instead' % (Database.__class__, self.mydatasource.connection.__class__))
