import os
import logging
import datetime

from django.conf import settings
from unittest import TestCase
import unittest

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fields import EmField
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType
from EditorialModel.types import EmType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields_types import Em_Field_Type
from EditorialModel.fieldtypes import *

from Database.sqlsetup import SQLSetup
from Database.sqlwrapper import SqlWrapper
from Database.sqlquerybuilder import SqlQueryBuilder
from Database import sqlutils

import sqlalchemy as sqla

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

## SetUpModule
#
# This function is called once for this module.
# It is designed to overwrite the database configurations, and prepare objects for test_case initialization
def setUpModule():
    # Overwriting the database parameters to make tests
    settings.LODEL2SQLWRAPPER['db'] = {
        'default':{
            'ENGINE': 'sqlite',
            'NAME': '/tmp/roland.testdb.sqlite'
        }
    }

    logging.basicConfig(level=logging.CRITICAL)

## FieldTestCase (Class)
#
# The parent class of all other test cases for the fields module.
# It defines a SetUp function and some utility functions for EmField tests.
class FieldTestCase(TestCase):

    def setUp(self):
        sqls = SQLSetup()
        sqls.initDb()

        # Generation of the test data
        self.testClass = EmClass.create("testclass1",EmClassType.entity)
        self.testClassUid = self.testClass.uid

        self.testFieldType = EmField_integer()

        self.testFieldgroup = EmFieldGroup.create('fieldgrp1',self.testClass)

        pass


    ## Get_Field_Type_Record (Function)
    #
    # Returns associations between field and type from the em_field_type table
    #
    # @param field EmField: Field object
    # @param type EmType: Type object
    # @return list of found associations
    def get_field_type_record(self, field, type):
        return self._get_field_type_record_Db(field, type)

    ## _Get_Field_Type_Record_Db (Function)
    #
    # Queries the database to get the record from the em_field_type table corresponding to a given field and type
    # @param field EmField: Field object
    # @param type EmType: Type object
    # @return found associations
    def _get_field_type_record_Db(self, field, type):
        sqlwrapper = SqlWrapper(read_db='default', write_db='default', alchemy_logs=False)
        sql_builder = SqlQueryBuilder(sql_wrapper, 'em_field_type')
        sql_builder.Select().From('em_field_type').Where('em_field_type.field_id=%s' % field.uid).Where('em_field_type.type_id=%s' % type.uid)
        records = sql_builder.Execute().fetchall()
        field_type_records = []
        for record in records:
            field_type_records.append(dict(zip(record.keys(),record)))

        return field_type_records


    ## Get_Field_Records (Function)
    #
    # Returns the list of fields corresponding to a given uid
    #
    # @param uid int: Global identifier of the field
    # @return list of found fields
    def get_field_records(self,uid):
        return self._get_field_records_Db(uid)

    ## _Get_Field_Records_Db (Function)
    #
    # Queries the database to get the list of fields for a given uid
    #
    # @param uid int: Global identifier of the field
    # @return list of found fields
    def _get_field_records_Db(self,uid):
        sql_wrapper = SqlWrapper(read_db='default', write_db='default', alchemy_logs=False)
        sql_builder = SqlQueryBuilder(sql_wrapper, 'em_field')
        sql_builder.Select(('uid'))
        sql_builder.From('em_field')
        sql_builder.Where('em_field.uid=%s' % uid)
        records = sql_builder.Execute().fetchall()
        field_records = []
        for record in records:
            field_records.append(dict(zip(record.keys(), record)))

        return field_records

    ## Get_table_columns (Function)
    #
    # Returns the columns list of a table
    #
    # @param table_name str: Name of the table
    # @return list of columns
    def get_table_columns(self,table_name):
        return self._get_table_columns_Db(table_name)

    ## _Get_table_columns_Db (Function)
    #
    # Queries the database to get the list of columns of a table
    #
    # @param table_name str: Name of the table
    # @return list of columns
    def _get_table_columns_Db(self, table_name):
        table = sqla.Table(table_name, self.dber)
        return table.c

## TestField (Class)
#
# The test class for the fields module
class TestField(FieldTestCase):

    ## TestFieldName (Function)
    #
    # The field's name is correctly populated
    def testFieldName(self):
        emField = EmField('testfield')
        self.assertEqual(emField.name,'testfield')

    ## Test_create (Function)
    #
    # tests the creation process of a field
    def testCreate(self):

        field = EmField.create('testfield1', self.testFieldgroup, self.testFieldType)
        fieldUid = field.uid
        # We check that the field has been added in the em_field table
        field_records = self.get_field_records(fieldUid)
        self.assertEqual(len(field_records),1)
        self.assertEqual(fieldUid,field_record[0]['uid'])
        self.assertEqual(field.name,field_record[0]['name'])

        # We check that the field has been added as a column in the corresponding table
        field_table_columns = self.get_table_columns(field.get_class_table())
        field_column_args = EmField_boolean.sqlalchemy_args()
        field_column_args['name']='testfield1'
        field_column = sqla.Column(**field_column_args)
        self.assertIn(field_column,field_table_columns)
        pass
