import os
import logging
import datetime

from django.conf import settings
from unittest import TestCase
import unittest

from EditorialModel.types import EmType
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType
from EditorialModel.components import EmComponent
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fieldtypes import *
from EditorialModel.fields_types import Em_Field_Type
from EditorialModel.fields import EmField
from EditorialModel.test.utils import *
from Database import sqlutils

import sqlalchemy as sqla

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")
TEST_TYPE_DBNAME = 'test_em_type_db.sqlite'

def setUpModule():
    logging.basicConfig(level=logging.CRITICAL)

    initTestDb(TEST_TYPE_DBNAME)
    setDbConf(TEST_TYPE_DBNAME)

    saveDbState(TEST_TYPE_DBNAME)

def tearDownModule():
    cleanDb(TEST_TYPE_DBNAME)
    pass

class TypeTestCase(TestCase):

    def setUp(self):

        self.emclass1 = EmClass.create("entity1", EmClassType.entity)
        self.emclass2 = EmClass.create("entity2", EmClassType.entity)

        self.emtype = EmType.create('type1',self.emclass2)
        self.emfieldgroup = EmFieldGroup.create('fieldgroup1',self.emclass1)
        self.emfieldtype = get_field_type('integer')
        self.emfield = EmField.create(name='field1', fieldgroup=self.emfieldgroup, fieldtype=self.emfieldtype, rel_to_type_id=self.emtype.uid)

        restoreDbState(TEST_TYPE_DBNAME)
        pass

class TestSelectField(TypeTestCase):
    def testSelectField(self):
        self.emtype.select_field(self.emfield)
        self.assertIsNotNone(Em_Field_Type(self.emtype.uid, self.emfield.uid))

    def testUnselectField(self):
        self.emtype.unselect_field(self.emfield)
        self.assertFalse(Em_Field_Type(self.emtype.uid, self.emfield.uid).exists())

