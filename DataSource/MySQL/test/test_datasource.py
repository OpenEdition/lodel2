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

from Lodel.settings import Settings
import DataSource.MySQL
from DataSource.MySQL.leapidatasource import LeapiDataSource as DataSource
import DataSource.MySQL.utils as db_utils
from EditorialModel.classtypes import common_fields, relations_common_fields
from EditorialModel.fieldtypes.generic import MultiValueFieldType

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
            #test with arguments
            conn_args = { 'hello': 'world', 'answer': 42 }
            DataSource(mosql, **conn_args)
            mock_db.assert_called_once_with(mosql, **conn_args)

            mock_db.reset_mock()
    
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

            class_table_datas = {
                fname: random.randint(42,1337)
                for fname in letype.fieldlist(complete = False)
                if not isinstance(letype.fieldtypes()[fname], MultiValueFieldType)
            }
            i18n = dict()
            for fname in letype.fieldlist():
                if isinstance(letype.fieldtypes()[fname], MultiValueFieldType):
                    i18n[fname] = {'fre': 'bonjour', 'eng': 'hello'}
                    class_table_datas[fname] = i18n[fname]
            object_table_datas = { 'string': random.randint(-42,42) }
            
            # build the insert datas argument
            insert_datas = copy.copy(object_table_datas)
            insert_datas.update(class_table_datas)

            with patch.object(mosql_Query, '__call__', return_value=sql_query) as mock_insert:
                with patch.object(db_utils, 'query', return_value=cursor_mock) as mock_utils_query:
                    # call the insert() method
                    datasource.insert(letype, **insert_datas)

                    # construct expected datas for object table insert
                    object_table_datas['class_id'] = letype._class_id
                    object_table_datas['type_id'] = letype._type_id
                    # construct expected datas used in class table insert
                    class_table_datas['lodel_id'] = lodel_id
                    for fname in i18n:
                        del(class_table_datas[fname])

                    expected_calls = [
                        # insert in object table call
                        call(
                            db_utils.common_tables['object'],
                            object_table_datas
                        ),
                        # insert in class specific table call
                        call(
                            db_utils.object_table_name(letype._leclass.__name__),
                            class_table_datas
                        ),
                    ]
                    i18n_calls = dict()
                    for fname, fval in i18n.items():
                        keyname = letype.fieldtypes()[fname].keyname
                        if not keyname in i18n_calls:
                            i18n_calls[keyname] = dict()
                        for lang, val in fval.items():
                            if not lang in i18n_calls[keyname]:
                                i18n_calls[keyname][lang] = dict()
                            i18n_calls[keyname][lang][fname] = val
                    real_i18n_calls = []
                    for keyname, kval in i18n_calls.items():
                        table_name = db_utils.multivalue_table_name(
                            db_utils.object_table_name(letype._leclass.__name__),
                            keyname
                        )
                        for lang, value in kval.items():
                            value[keyname] = lang
                            value[letype.uidname()] = lodel_id
                            expected_calls.append(call(
                                    table_name,
                                    value
                                )
                            )
                    expected_utils_query_calls = [
                        call(datasource.connection, sql_query),
                        call(datasource.connection, sql_query),
                    ]

                    mock_insert.assert_has_calls(expected_calls, any_order = False)
                    mock_utils_query.assert_has_calls(expected_utils_query_calls)

    def test_select_leobject(self):
        """ Test select method on leobject without relational filters """
        from dyncode import LeObject, Article, Textes
        
        # Utils var and stuff to make tests queries write easier
        
        # lodel_id field name
        lodel_id = LeObject.uidname()
        # pre-fetch tables name to make the tests_queries
        table_names = {
            LeObject: db_utils.common_tables['object'],
            Article: db_utils.object_table_name(Article._leclass.__name__),
            Textes: db_utils.object_table_name(Textes.__name__),
        }
        # lodel_id name to be use in joins (leobject side)
        join_lodel_id = db_utils.column_prefix(table_names[LeObject], lodel_id)
        # lodel_id name to be use in joins (leclass side)
        def cls_lodel_id(cls): return db_utils.column_prefix(table_names[cls], lodel_id)

        tests_queries = [
            # call leobject.select(fields = ['lodel_id', 'string'], filters = [])
            (
                #field_list details
                {
                    'leobject': [lodel_id, 'string'],
                    'leclass': [],
                },
                #Select args
                {
                    'target_cls': LeObject,
                    'filters': [],
                    'rel_filters': [],
                },
                # expt args
                {
                    'where':{},
                    'joins':None, #Expected call on Query.__call__ (called when we call left_join)
                }
            ),
            # call leobject.select(fields = ['lodel_id', 'string'], filters = ['lodel_id = 42', 'string = "hello"', 'rank > 1'])
            (
                {
                    'leobject': [lodel_id, 'string'],
                    'leclass': [],
                },
                {
                    'target_cls': LeObject,
                    'filters': [
                        (lodel_id,'=', 42),
                        ('string', '=', 'Hello'),
                        ('modification_date', '>', 1),
                    ],
                    'rel_filters': [],
                },
                {
                    'where':{
                        (
                            db_utils.column_prefix(table_names[LeObject], lodel_id),
                            '='
                        ): 42,
                        (
                            db_utils.column_prefix(table_names[LeObject], 'string'),
                            '='
                        ): 'Hello',
                        (
                            db_utils.column_prefix(table_names[LeObject], 'modification_date'),
                            '>'
                        ): 1
                    },
                    'joins':None, #Expected call on Query.__call__ (called when we call left_join)
                }
            ),
        ]

        # mock the database module to avoid connection tries
        dbmodule_mock = Mock()

        datasource = DataSource(module=dbmodule_mock, conn_args = {})
        sql_query = 'SELECT foo FROM LeObject' # Fake return of mosql.select()

        for fields_details, select_args, expt_args in tests_queries:
            mosql_query_return_value = sql_query
            with patch.object(mosql_Query, '__call__', return_value=mosql_query_return_value) as mock_select:
                with patch.object(db_utils, 'query') as mock_utils_query:
                    # building the field_list argument
                    select_args['field_list'] = copy.copy(fields_details['leobject'])
                    select_args['field_list'] += fields_details['leclass']
                    # call
                    datasource.select(**select_args)

                    # building the select expected argument
                    select_arg = [ db_utils.column_prefix(db_utils.common_tables['object'], fname) for fname in fields_details['leobject'] ]
                    if len(fields_details['leclass']) > 0:
                        leclass = select_args['target_cls']
                        leclass = leclass._leclass if leclass.is_letype() else leclass
                        table_name = db_utils.object_table_name(leclass.__name__)
                        select_arg += [ db_utils.column_prefix(table_name, field_name) for field_name in fields_details['leclass'] ]
                    
                    if expt_args['joins'] is None:
                        # If the call is made with LeObject as target class no joins call is made
                        mock_select.assert_called_once_with(
                            db_utils.common_tables['object'],
                            select= select_arg,
                            where=expt_args['where'],
                            joins=[]
                        )
                    else:
                        # Else there has to be 2 calls, 1 for the join another for the select
                        expected_calls = [
                            expt_args['joins'],
                            call(
                                db_utils.common_tables['object'],
                                select= select_arg,
                                where=expt_args['where'],
                                joins=[mosql_query_return_value]
                            )
                        ]
                        mock_select.assert_has_calls(expected_calls, any_order=False)
                    
                    # Tests that the query is really sent to the query method
                    mock_utils_query.assert_called_once_with(
                        datasource.connection,
                        sql_query
                    )
