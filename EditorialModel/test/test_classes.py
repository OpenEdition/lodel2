"""
    Tests for the EmClass class
"""

import os
import logging

from unittest import TestCase
import unittest

from django.conf import settings
from EditorialModel.components import EmComponentNotExistError
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.types import EmType
from EditorialModel.fields import EmField
import EditorialModel.fieldtypes  as fieldTypes
from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.migrationhandler.django import DjangoMigrationHandler
#from Database import sqlutils, sqlsetup
#import sqlalchemy as sqla


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")
EM_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'me.json')
EM_TEST_OBJECT = None

## run once for this module
# define the Database for this module (an sqlite database)
def setUpModule():
    global EM_TEST_OBJECT
    EM_TEST_OBJECT = Model(EmBackendJson(EM_TEST))  # , migration_handler=DjangoMigrationHandler('LodelTestInstance'))
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
        testClass = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testclass1', 'classtype': EmClassType.entity['name']})

        #We check the uid
        self.assertEqual(testClass.uid, 18)

        # We check that the class has been added in the right list in the model object
        class_components_records = EM_TEST_OBJECT.components(EmClass)
        self.assertIn(testClass, class_components_records)

        # the name should be the one given
        testClass = EM_TEST_OBJECT.component(testClass.uid)
        self.assertEqual(testClass.name, 'testclass1')

        # the classtype should have the name of the EmClassType
        testClass = EM_TEST_OBJECT.component(testClass.uid)
        self.assertEqual(testClass.classtype, EmClassType.entity['name'])


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
        for i, class_object in enumerate(self.emclasses):
            self.assertTrue(EM_TEST_OBJECT.delete_component(class_object.uid), "delete method didn't return True but the class has no fieldgroups")

        # TODO check : "table still exists but the class was deleted"
        # TODO check : "table doesn't exist but the class was not deleted"


    # tests if delete refuse to delete if a class had fieldgroups
    def test_table_refuse_delete(self):
        """ Test delete on an EmClass that has fieldgroup """
        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__,{'name': 'testfgclass1', 'classtype': EmClassType.entity['name']})
        fieldgroup = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'testsubfg1', 'class_id': test_class.uid})
        self.assertFalse(EM_TEST_OBJECT.delete_component(test_class.uid), "delete method returns True but the class has fieldgroup(s)")

        # TODO check : "table has been deleted but the class has fieldgroup"

        try:
            EM_TEST_OBJECT.component(test_class.uid)
        except EmComponentNotExistError:
            self.fail("The class has been deleted but it has fieldgroups")


# Interface to fieldgroups
class TestEmClassFieldgrousp(ClassesTestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        self.test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testClassFg', 'classtype': EmClassType.entity['name']})

    # tests if fieldgroups() returns a list of EmFieldGroup
    def test_fieldgroups(self):
        """ Tests if fieldgroups method returns the right list of EmFieldGroup """
        test_class = EM_TEST_OBJECT.component(self.test_class.uid)
        fg1 = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'testClassFg1', 'class_id': test_class.uid})
        fg2 = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'testClassFg2', 'class_id': test_class.uid})

        fieldgroups = test_class.fieldgroups()
        self.assertIsInstance(fieldgroups, list)
        for fieldgroup in fieldgroups:
            self.assertIsInstance(fieldgroup, EmFieldGroup)

    # with no fieldgroups, fieldgroups() should return an empty list
    def test_no_fieldgroups(self):
        """ Test fieldgroups method on an empty EmClass """
        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testClassFg3', 'classtype': EmClassType.entity['name']})
        fieldgroups = test_class.fieldgroups()
        self.assertEqual(fieldgroups, [])


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
        t1 = EM_TEST_OBJECT.create_component(EmType.__name__, {'name': 'testClassType1', 'class_id': test_class.uid})
        t2 = EM_TEST_OBJECT.create_component(EmType.__name__, {'name': 'testClassType2', 'class_id': test_class.uid})
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
        fg = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'testClassFieldsFg', 'class_id': test_class.uid})
        f1 = EM_TEST_OBJECT.create_component(EmField.__name__, {'name': 'f1', 'fieldgroup_id': fg.uid, 'fieldtype': 'char'})
        f2 = EM_TEST_OBJECT.create_component(EmField.__name__, {'name': 'f2', 'fieldgroup_id': fg.uid, 'fieldtype': 'char'})
        fields = test_class.fields()
        self.assertIsInstance(fields, list)
        for field in fields:
            self.assertIsInstance(field, EmField)

    # with no field fields() should return an empty list
    def test_no_fields(self):
        """ Testing fields method on an EmClass with no associated fields """
        test_class = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testClassNoFields', 'classtype': EmClassType.entity['name']})
        fields = test_class.fields()
        self.assertEqual(fields, [])


# Creating a new EmClass should :
# - create a table named like the created EmClass
# - insert a new line in em_classes
@unittest.skip("Not implemented yet")
class TestEmClassLinkType(ClassesTestCase):

    # create a new EmClass, then test on it
    @classmethod
    def setUpClass(cls):
        ClassesTestCase.setUpClass()
        testEntity = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testEntity', 'classtype': EmClassType.entity['name']})
        testEntry = EM_TEST_OBJECT.create_component(EmClass.__name__, {'name': 'testEntry', 'classtype': EmClassType.entry['name']})
        keywords = EM_TEST_OBJECT.create_component(EmType.__name__, {'name': 'keywords', 'class_id': testEntry.uid})
        testEntity.link_type(keywords)

'''

    # test if a table 'testEntity_keywords' was created
    # should be able to select on the created table
    def test_table_classes_types(self):
        """ Test if a table 'testEntity_keywords' was created """
        conn = sqlutils.get_engine().connect()
        a = sqlutils.meta(conn)
        try:
            newtable = sqla.Table('testEntity_keywords', sqlutils.meta(conn))
            req = sqla.sql.select([newtable])
            res = conn.execute(req)
            res = res.fetchall()
            conn.close()
        except:
            self.fail("unable to select table testEntity_keywords")
        self.assertEqual(res, [])

    # test if we can retrieve the linked type
    def test_linked_types(self):
        """ Test linked_types """
        testEntity = EmClass('testEntity')
        linked_types = testEntity.linked_types()
        self.assertEqual(linked_types[0].name, 'keywords')
'''