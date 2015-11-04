"""
    Tests for the EmClass class
"""

import os
import logging

from unittest import TestCase
import unittest

import EditorialModel
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType
from EditorialModel.types import EmType
from EditorialModel.fields import EmField
from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")
EM_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'me.json')
EM_TEST_OBJECT = None


## run once for this module
def setUpModule():
    global EM_TEST_OBJECT
    #EM_TEST_OBJECT = Model(EmBackendJson(EM_TEST), migration_handler=DjandoMigrationHandler('LodelTestInstance'))
    EM_TEST_OBJECT = Model(EmBackendJson(EM_TEST), migration_handler=DummyMigrationHandler())
    logging.basicConfig(level=logging.CRITICAL)


class ClassesTestCase(TestCase):

    # run before every instanciation of the class
    @classmethod
    def setUpClass(cls):
        pass
        #sqlsetup.init_db()

    # run before every function of the class
    def setUp(self):
        pass


# creating an new EmClass should
# - create a table named like the created EmClass
# - insert a new line in em_classes
class TestEmClassCreation(ClassesTestCase):

    # create a new EmClass, then test on it
    def test_create(self):
        ClassesTestCase.setUpClass()
        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testclass1', 'classtype': EmClassType.entity['name']})

        # We check that the class has been added in the right list in the model object
        class_components_records = EM_TEST_OBJECT.components(EmClass)
        self.assertIn(test_class, class_components_records)

        # the name should be the one given
        test_class = EM_TEST_OBJECT.component(test_class.uid)
        self.assertEqual(test_class.name, 'testclass1')

        # the classtype should have the name of the EmClassType
        test_class = EM_TEST_OBJECT.component(test_class.uid)
        self.assertEqual(test_class.classtype, EmClassType.entity['name'])
    
    def test_default_fields(self):
        """ Test if the default + common_fields are created when an EmClass is created """
        classtype = EmClassType.entity['name']
        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testdefaultfieldclass', 'classtype': classtype})
        ctype = EditorialModel.classtypes.EmClassType.get(classtype)
        default_fields = ctype['default_fields']
        default_fields.update(EditorialModel.classtypes.common_fields)
        
        fnames = [ f.name for f in test_class.fields() ]
        self.assertEqual(sorted(fnames), sorted(list(default_fields.keys())))


# Testing class deletion (and associated table drop)
class TestEmClassDeletion(ClassesTestCase):

    def setUp(self):
        self.names = ['testClasse1', 'testClasse2', 'testClasse3']
        self.emclasses = []
        self.emclasses.append(EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': self.names[0], 'classtype': EmClassType.entity['name']}))
        self.emclasses.append(EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': self.names[1], 'classtype': EmClassType.entry['name']}))
        self.emclasses.append(EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': self.names[2], 'classtype': EmClassType.person['name']}))

    # tests if the table is deleted after a call to delete
    def test_table_delete(self):
        """ Test associated table deletion on EmClass deletion """
        for _, class_object in enumerate(self.emclasses):
            self.assertTrue(EM_TEST_OBJECT.delete_component(class_object.uid), "delete method didn't return True but the class has no fieldgroups")

        # TODO check : "table still exists but the class was deleted"
        # TODO check : "table doesn't exist but the class was not deleted"

    # tests if delete refuse to delete if a class had fieldgroups
    def test_table_refuse_delete(self):
        """ Test delete on an EmClass that has fieldgroup """
        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testfgclass1', 'classtype': EmClassType.entity['name']})

        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testClassFalseEmpty', 'classtype': EmClassType.entity['name']})
        foo_field = EM_TEST_OBJECT.create_component('EmField', {'name': 'ahah', 'fieldtype':'char', 'class_id':test_class.uid})
        self.assertFalse(EM_TEST_OBJECT.delete_component(test_class.uid), "delete method returns True but the class has a non-default field")

        # TODO check : "table has been deleted but the class has fieldgroup"

        try:
            EM_TEST_OBJECT.component(test_class.uid)
        except Exception:
            self.fail("The class has been deleted but it has non-default field in the default fieldgroup")


# Interface to types
class TestEmClassTypes(ClassesTestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        self.test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testClassType', 'classtype': EmClassType.entity['name']})

    # tests if types() returns a list of EmType
    def test_types(self):
        """ Tests if types method returns the right list of EmType """
        test_class = EM_TEST_OBJECT.component(self.test_class.uid)
        EM_TEST_OBJECT.create_component(EmType.__name__, {'name': 'testClassType1', 'class_id': test_class.uid})
        EM_TEST_OBJECT.create_component(EmType.__name__, {'name': 'testClassType2', 'class_id': test_class.uid})
        types = test_class.types()
        self.assertIsInstance(types, list)
        for t in types:
            self.assertIsInstance(t, EmType)

    # with no type, types() should return an empty list
    def test_no_types(self):
        """ Test types method on an EmClass with no associated types """
        test_class = EM_TEST_OBJECT.component(self.test_class.uid)
        types = test_class.types()
        self.assertEqual(types, [])


# interface to fields
class TestEmClassFields(ClassesTestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        self.test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testClassFields', 'classtype': EmClassType.entity['name']})

    # tests if fields() returns a list of EmField
    def test_fields(self):
        """ testing fields method """
        test_class = EM_TEST_OBJECT.component(self.test_class.uid)
        EM_TEST_OBJECT.create_component(EmField.__name__, {'name': 'f1', 'class_id': test_class.uid, 'fieldtype': 'char'})
        EM_TEST_OBJECT.create_component(EmField.__name__, {'name': 'f2', 'class_id': test_class.uid, 'fieldtype': 'char'})
        fields = test_class.fields()
        self.assertIsInstance(fields, list)
        for field in fields:
            self.assertIsInstance(field, EmField)

    # with no field fields() should return an empty list
    def test_default_fields(self):
        """ Testing fields method on an EmClass with only defaults fields """
        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testClassNoFields', 'classtype': EmClassType.entity['name']})
        fields = test_class.fields()
    
        for fname in [f.name for f in fields]:
            self.assertIn(fname, EmClassType.get(test_class.classtype)['default_fields'].keys())


# Creating a new EmClass should :
# - create a table named like the created EmClass
# - insert a new line in em_classes
class TestEmClassLinkType(ClassesTestCase):

    # create a new EmClass, then test on it
    @classmethod
    def setUpClass(cls):
        ClassesTestCase.setUpClass()
        test_entity = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testEntity', 'classtype': EmClassType.entity['name']})
        test_entry = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testEntry', 'classtype': EmClassType.entry['name']})

    def testLinkedTypes(self):
        """ Test the EmClass.linked_types() method """
        for field, linked_type in [ (f, EM_TEST_OBJECT.component(f.rel_to_type_id)) for f in EM_TEST_OBJECT.components(EmField) if 'rel_to_type_id' in f.__dict__]:
            self.assertIn(linked_type, field.em_class.linked_types())

