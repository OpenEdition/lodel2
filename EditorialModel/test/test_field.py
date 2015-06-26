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
            'NAME': '/tmp/lodel2_test_db.sqlite'
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
        self.testFieldType = EmField_integer()
        self.testFieldgroup = EmFieldGroup.create('fieldgrp1',self.testClass)
        self.testType = EmType.create('testtype1',self.testClass)

    ## Get_Field_Records (Function)
    #
    # Returns the list of fields corresponding to a given uid
    #
    # @param field EmField: EmField object
    # @return Number of found records
    def get_field_records(self,field):
        return self._get_field_records_Db(field)

    ## _Get_Field_Records_Db (Function)
    #
    # Queries the database to get the list of fields for a given uid
    #
    # @param field EmField: EmField object
    # @return Number of found records
    def _get_field_records_Db(self,field):
        dbe = EmComponent.getDbE()
        fieldtable = sqla.Table(EmField.table, sqlutils.meta(dbe))
        conn = dbe.connect()
        req = fieldtable.select().where(fieldtable.c.uid==field.uid).where(fieldtable.c.name==field.name)
        res = conn.execute(req).fetchall()

        return len(res)

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
        table = sqla.Table(table_name, sqlutils.meta(EmComponent.getDbE()))
        return table.c

## TestField (Class)
#
# The test class for the fields module
class TestField(FieldTestCase):

    ## Test_create (Function)
    #
    # tests the creation process of a field
    def testCreate(self):
        '''
        field_values = {
            'name':'testfield1',
            'fieldgroup_id' : self.testFieldgroup.uid,
            'fieldtype' : self.testFieldType,
            'rel_to_type_id': self.testType.uid
        }
        '''
        field = EmField.create(name='testfield1', fieldgroup=self.testFieldgroup, fieldtype=self.testFieldType)

        # We check that the field has been added in the em_field table
        field_records = self.get_field_records(field)
        self.assertGreater(field_records,0)

        # We check that the field has been added as a column in the corresponding table
        field_table_columns = self.get_table_columns(field.get_class_table())
        field_column_args = self.testFieldType.sqlalchemy_args()
        field_column_args['name']='testfield1'
        field_column = sqla.Column(**field_column_args)
        self.assertIn(field_column.name, field_table_columns)
        pass
