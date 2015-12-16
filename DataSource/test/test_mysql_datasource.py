"""
    Tests for MySQL Datasource
"""

import random
import copy

import unittest
import unittest.mock as mock
from unittest import TestCase
from unittest.mock import patch, Mock, call

import mosql
import mosql.db
from mosql.util import Query as mosql_Query
import pymysql

import leapi.test.utils #Code generation functions

import Lodel.settings
import DataSource.MySQL
from DataSource.MySQL.leapidatasource import LeDataSourceSQL as DataSource
from DataSource.MySQL.common_utils import MySQL as db_utils
from EditorialModel.classtypes import common_fields, relations_common_fields

class DataSourceTestCase(TestCase):
    #Dynamic code generation & import
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

    def test_init(self):
        """ Test __init__ for datasource """
        with patch.object(mosql.db.Database, '__init__', return_value=None) as mock_db:
            #Test __init__ without arguments
            DataSource()
            conn_args = db_utils.connections['default']
            db_module = conn_args['module']
            del(conn_args['module'])
            mock_db.assert_called_once_with(db_module, **conn_args)

            mock_db.reset_mock()
            #test with arguments
            conn_args = { 'hello': 'world', 'answer': 42 }
            DataSource(mosql, conn_args)
            mock_db.assert_called_once_with(mosql, **conn_args)

            mock_db.reset_mock()

            DataSource(conn_args = conn_args)
            mock_db.assert_called_once_with(pymysql, **conn_args)
    
    def test_insert_leobject(self):
        """ Test the insert method on LeObjects """
        from dyncode import Article, Personne, Rubrique

        for letype in [Article, Personne, Rubrique]:
            lodel_id = random.randint(0,4096) # Choose a random lodel_id
            
            # Mock the cursor to superseed the lastrowid property
            cursor_mock = Mock()
            cursor_mock.lastrowid = lodel_id
            # Mock the cursor() call on connection
            cursor_call_mock = Mock(return_value=cursor_mock)
            # Mock the connection to set the cursor() call mock
            connection_mock = Mock()
            connection_mock.cursor = cursor_call_mock
            # Mock the connect() call on dbmodule to bla bla
            connect_call_mock = Mock(return_value=connection_mock)
            # Mock the db module to set the connection mock (on connect() call)
            dbmodule_mock = Mock()
            dbmodule_mock.connect = connect_call_mock

            datasource = DataSource(module=dbmodule_mock, conn_args = {})

            sql_query = 'SELECT wow FROM splendid_table'

            class_table_datas = { 'title': 'foo', 'number': 42 }
            object_table_datas = { 'string': random.randint(-42,42) }
            
            # build the insert datas argument
            insert_datas = copy.copy(object_table_datas)
            insert_datas.update(class_table_datas)

            with patch.object(mosql_Query, '__call__', return_value=sql_query) as mock_insert:
                with patch.object(db_utils, 'query', return_value=cursor_mock) as mock_utils_query:
                    #mock_utils_query = Mock()
                    #db_utils.query = mock_utils_query

                    # call the insert() method
                    datasource.insert(letype, **insert_datas)

                    # construct expected datas for object table insert
                    object_table_datas['class_id'] = letype._class_id
                    object_table_datas['type_id'] = letype._type_id
                    # construct expected datas used in class table insert
                    class_table_datas['lodel_id'] = lodel_id

                    expected_calls = [
                        # insert in object table call
                        call(
                            db_utils.objects_table_name,
                            object_table_datas
                        ),
                        # insert in class specific table call
                        call(
                            db_utils.get_table_name_from_class(letype._leclass.__name__),
                            class_table_datas
                        ),
                    ]

                    expected_utils_query_calls = [
                        call(datasource.connection, sql_query),
                        call(datasource.connection, sql_query),
                    ]

                    mock_insert.assert_has_calls(expected_calls, any_order = False)
                    mock_utils_query.assert_has_calls(expected_utils_query_calls)


