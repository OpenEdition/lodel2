import os
import logging
import datetime

from django.conf import settings
from unittest import TestCase
import unittest

from EditorialModel.types import EmType
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType, EmNature
from EditorialModel.components import EmComponent, EmComponentNotExistError
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

    emclass1 = EmClass.create("entity1", EmClassType.entity)
    emclass2 = EmClass.create("entity2", EmClassType.entity)
    emtype = EmType.create(name='type1', em_class=emclass2)
    EmType.create(name='type2', em_class=emclass2)
    EmType.create(name='type3', em_class=emclass2)
    emfieldgroup = EmFieldGroup.create(name='fieldgroup1', em_class=emclass1)
    emfieldtype = get_field_type('integer')
    EmField.create(name='field1', fieldgroup=emfieldgroup, fieldtype=emfieldtype, rel_to_type_id=emtype.uid)

    saveDbState(TEST_TYPE_DBNAME)

def tearDownModule():
    cleanDb(TEST_TYPE_DBNAME)
    pass

class TypeTestCase(TestCase):
    
    def setUp(self):
        restoreDbState(TEST_TYPE_DBNAME)
        self.emclass1 = EmClass("entity1")
        self.emclass2 = EmClass("entity2")
        self.emtype = EmType('type1')
        self.emtype2 = EmType('type2')
        self.emtype3 = EmType('type3')
        self.emfieldgroup = EmFieldGroup('fieldgroup1')
        self.emfieldtype = get_field_type('integer')
        self.emfield = EmField('field1')


class TestSelectField(TypeTestCase):
    def testSelectField(self):
        self.emtype.select_field(self.emfield)
        self.assertIsNotNone(Em_Field_Type(self.emtype.uid, self.emfield.uid))

    def testUnselectField(self):
        self.emtype.unselect_field(self.emfield)
        self.assertFalse(Em_Field_Type(self.emtype.uid, self.emfield.uid).exists())

class TestLinkedTypes(TypeTestCase):
    def testLinkedtypes(self):
        self.emtype.add_superior(self.emtype2, EmNature.PARENT)
        self.emtype3.add_superior(self.emtype, EmNature.PARENT)

        linked_types = self.emtype.linked_types()

        self.assertEqual(len(linked_types),2)
        self.assertNotIn(self.emtype,linked_types)
        self.assertIn(self.emtype2, linked_types)
        self.assertIn(self.emtype3, linked_types)

class TestDeleteTypes(TypeTestCase):
    @unittest.skip("Test invalid, le type n'existe pas")
    def testDeleteTypes(self):
        type_name = self.emtype.name
        self.emtype.delete()
        with self.assertRaises(EmComponentNotExistError, msg="Type not deleted"):
            EmType(type_name)
