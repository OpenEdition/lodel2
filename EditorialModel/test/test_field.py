import os

from unittest import TestCase
from EditorialModel.fields import EmField
from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson

EM_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'me.json')
EM_TEST_OBJECT = None


## SetUpModule
#
# This function is called once for this module.
# It is designed to overwrite the database configurations, and prepare objects for test_case initialization
def setUpModule():
    global EM_TEST_OBJECT
    EM_TEST_OBJECT = Model(EmBackendJson(EM_TEST))
    #initTestDb(TEST_FIELD_DBNAME)
    #setDbConf(TEST_FIELD_DBNAME)
    #logging.basicConfig(level=logging.CRITICAL)


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
        self.test_fieldgroup = EM_TEST_OBJECT.component(3)


## TestField (Class)
#
# The test class for the fields module
class TestField(FieldTestCase):

    ## Test_create (Function)
    #
    # tests the creation process of a field
    def test_create(self):

        field = EM_TEST_OBJECT.create_component(EmField.__name__, {'name': 'testfield1', 'fieldgroup_id': self.test_fieldgroup.uid, 'fieldtype': self.test_fieldtype})

        # We check that the field has been added
        field_records = EM_TEST_OBJECT.component(field.uid)
        self.assertIsNot(field_records, False)

        # We check that the field has been added in the right list in the model object
        field_components_records = EM_TEST_OBJECT.components(EmField)
        self.assertIn(field, field_components_records)

    ## Test_Deletion
    #
    # tests the deletion process of a field
    def test_deletion(self):
        fields = []
        field_names = ['field1', 'field2']

        # We create the two fields
        for name in field_names:
            fields.append(EM_TEST_OBJECT.create_component(EmField.__name__, {'name': name, 'fieldgroup_id': self.test_fieldgroup.uid, 'fieldtype': self.test_fieldtype}))

        for field in fields:
            # We check if the delete process was performed to the end
            self.assertTrue(EM_TEST_OBJECT.delete_component(field.uid))

            # We check that the field object is not in the editorial model anymore
            self.assertFalse(EM_TEST_OBJECT.component(field.uid))

            # We check that the field object is not in the EmField components list
            field_components_records = EM_TEST_OBJECT.components(EmField)
            self.assertNotIn(field, field_components_records)
