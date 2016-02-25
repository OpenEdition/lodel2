import os

import unittest
from unittest import TestCase
from EditorialModel.fields import EmField
from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.exceptions import EmComponentCheckError

EM_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'me.json')
EM_TEST_OBJECT = None


## SetUpModule
#
# This function is called once for this module.
def setUpModule():
    global EM_TEST_OBJECT
    EM_TEST_OBJECT = Model(EmBackendJson(EM_TEST))


def tearDownModule():
    #cleanDb(TEST_FIELD_DBNAME)
    pass


## FieldTestCase (Class)
#
# The parent class of all other test cases for the fields module.
# It defines a SetUp function and some utility functions for EmField tests.
class FieldTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.test_fieldtype = 'integer'
        self.test_class = EM_TEST_OBJECT.components('EmClass')[0]


## TestField (Class)
#
# The test class for the fields module
class TestField(FieldTestCase):

    ## Test_create (Function)
    #
    # tests the creation process of a field
    def test_create(self):

        field = EM_TEST_OBJECT.create_component(EmField.__name__, {'name': 'testfield1', 'class_id': self.test_class.uid, 'fieldtype': self.test_fieldtype})

        # We check that the field has been added
        field_records = EM_TEST_OBJECT.component(field.uid)
        self.assertIsNot(field_records, False)

        # We check that the field has been added in the right list in the model object
        field_components_records = EM_TEST_OBJECT.components(EmField)
        self.assertIn(field, field_components_records)

    def test_invalid_internal(self):
        """ Test that internal='object' is reserved for common_fields """
        with self.assertRaises(ValueError, msg="Only common_fields should be internal='object'"):
            field = EM_TEST_OBJECT.create_component(EmField.__name__, {'name': 'testbadinternal','internal': 'object', 'class_id': self.test_class.uid, 'fieldtype': self.test_fieldtype})

    @unittest.skip("rel2type are not uniq like this anymore")
    def test_double_rel2type(self):
        """ Test the rel2type unicity """
        em = EM_TEST_OBJECT
        emtype = em.components('EmType')[0]
        emclass = [c for c in em.components('EmClass') if c != emtype.em_class][0]

        f1 = em.create_component('EmField', {'name': 'testr2t', 'class_id': emclass.uid, 'fieldtype': 'rel2type', 'rel_to_type_id': emtype.uid})

        with self.assertRaises(EmComponentCheckError):
            f2 = em.create_component('EmField', {'name': 'testr2t2', 'class_id': emclass.uid, 'fieldtype': 'rel2type', 'rel_to_type_id': emtype.uid})

    def test_same_name(self):
        """ Test the name unicity is the same EmClass"""
        em = EM_TEST_OBJECT
        emtype = em.components('EmType')[0]
        emclass = [c for c in em.components('EmClass') if c != emtype.em_class][0]

        f1 = em.create_component('EmField', {'name': 'samename', 'class_id': emclass.uid, 'fieldtype': 'char'})

        with self.assertRaises(EmComponentCheckError):
            f2 = em.create_component('EmField', {'name': 'samename', 'class_id': emclass.uid, 'fieldtype': 'integer'} )

        

    ## Test_Deletion
    #
    # tests the deletion process of a field
    def test_deletion(self):
        fields = []
        field_names = ['field1', 'field2']

        # We create the two fields
        for name in field_names:
            fields.append(EM_TEST_OBJECT.create_component(EmField.__name__, {'name': name, 'class_id': self.test_class.uid, 'fieldtype': self.test_fieldtype}))

        for field in fields:
            # We check if the delete process was performed to the end
            self.assertTrue(EM_TEST_OBJECT.delete_component(field.uid))

            # We check that the field object is not in the editorial model anymore
            self.assertFalse(EM_TEST_OBJECT.component(field.uid))

            # We check that the field object is not in the EmField components list
            field_components_records = EM_TEST_OBJECT.components(EmField)
            self.assertNotIn(field, field_components_records)

    def test_emclass(self):
        """ Test if the EmField.em_class \@property method is correct """
        for field in EM_TEST_OBJECT.components(EmField):
            self.assertIn(field, field.em_class.fields())
