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

#from Database import sqlutils, sqlsetup
#import sqlalchemy as sqla


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")
EM_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'me.json')
EM_TEST_OBJECT = None

## run once for this module
# define the Database for this module (an sqlite database)
def setUpModule():
    global EM_TEST_OBJECT
    EM_TEST_OBJECT = Model(EmBackendJson(EM_TEST))
    logging.basicConfig(level=logging.CRITICAL)
    #settings.LODEL2SQLWRAPPER['db']['default'] = {'ENGINE':'sqlite', 'NAME':'/tmp/testdb.sqlite'}

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
        self.assertEqual(testClass.uid, 22)

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
        self.names = ['testClass1', 'testClass2', 'testClass3']
        EmClass.create(self.names[0], EmClassType.entity)
        EmClass.create(self.names[1], EmClassType.entry)
        EmClass.create(self.names[2], EmClassType.person)
        pass
    
    # test if the table is deleted after a call to delete
    def test_table_delete(self):
        """ Test associated table deletetion on EmClass deletion """
        dbe = sqlutils.get_engine()
        for i,class_name in enumerate(self.names):
            cur_class = EmClass(class_name)
            self.assertTrue(cur_class.delete(), "delete method didn't return True but the class has no fieldgroups")
            meta = sqlutils.meta(dbe)
            table_list = meta.tables.keys()
            for deleted_name in self.names[:i+1]:
                self.assertNotIn(deleted_name, table_list, "Table still exist but the class was deleted")
            for not_deleted_name in self.names[i+1:]:
                self.assertIn(not_deleted_name, table_list, "Table don't exist but the class was NOT deleted")
            with self.assertRaises(EmComponentNotExistError,msg="This EmClass should be deleted"):
                EmClass(class_name)
        pass
    
    # test if delete refuse to delete if a class had fieldgroups
    def test_table_refuse_delete(self):
        """ Test delete on an EmClass has fieldgroup """
        test_class = EmClass(self.names[0])
        fieldgroup = EmFieldGroup.create('fooFieldGroup', test_class)
        self.assertFalse(test_class.delete(), "delete method returns True but the class has fieldgroup")
        dbe = sqlutils.get_engine()
        meta = sqlutils.meta(dbe)
        self.assertIn(self.names[0], meta.tables, "Table has been deleted but the class has fieldgroup")
        try:
            EmClass(self.names[0])
        except EmComponentNotExistError:
            self.fail("The class has been deleted but it has fieldgroups")
        pass


# interface to fieldGroups
class TestEmClassFieldgroups(ClassesTestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        test_class = EmClass.create('testClass', EmClassType.entity)

    # test if fieldgroups() return a list of EmFieldGroup
    def test_fieldgroups(self):
        """ Test if fieldgroups method return the right list of EmFielGroup """
        test_class = EmClass('testClass')
        fg1 = EmFieldGroup.create('fg1', test_class)
        fg2 = EmFieldGroup.create('fg2', test_class)

        fieldgroups = test_class.fieldgroups()
        self.assertIsInstance(fieldgroups, list)
        for fieldgroup in fieldgroups:
            self.assertIsInstance(fieldgroup, EmFieldGroup)

    # with no fieldgroups fieldgroups() should return an empty list
    def test_no_fieldgroups(self):
        """ Test fielgroups method on an empty EmClass """
        test_class = EmClass('testClass')
        fieldgroups = test_class.fieldgroups()
        self.assertEqual(fieldgroups, [])

# interface to types
class TestEmClassTypes(ClassesTestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        test_class = EmClass.create('testClass', EmClassType.entity)

    # test if types() return a list of EmType
    def test_types(self):
        """ Test if types method return the right list of EmType """
        test_class = EmClass('testClass')
        t1 = EmType.create('t1', test_class)
        t2 = EmType.create('t2', test_class)

        types = test_class.types()
        self.assertIsInstance(types, list)
        for t in types:
            self.assertIsInstance(t, EmType)

    # with no type types() should return an empty list
    def test_no_types(self):
        """ Test types method on an EmClass with no associated types """
        test_class = EmClass('testClass')
        types = test_class.types()
        self.assertEqual(types, [])

# interface to fields
class TestEmClassFields(ClassesTestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        test_class = EmClass.create('testClass', EmClassType.entity)

    # test if fields() return a list of EmField
    def test_fields(self):
        """ Testing fields method """
        test_class = EmClass('testClass')
        fg = EmFieldGroup.create('fg', test_class)
        f1 = EmField.create('f1', fg, fieldTypes.EmField_char())
        f2 = EmField.create('f2', fg, fieldTypes.EmField_char())

        fields = test_class.fields()
        self.assertIsInstance(fields, list)
        for field in fields:
            self.assertIsInstance(field, EmField)

    # with no field fields() should return an empty list
    def test_no_fields(self):
        """ Testing fields method on an EmClass with no associated fields """
        test_class = EmClass('testClass')
        fields = test_class.fields()
        self.assertEqual(fields, [])

# creating an new EmClass should
# - create a table named like the created EmClass
# - insert a new line in em_classes
@unittest.skip("Not implemented yet")
class TestEmClassLinkType(ClassesTestCase):

    # create a new EmClass, then test on it
    @classmethod
    def setUpClass(cls):
        ClassesTestCase.setUpClass()
        testEntity = EmClass.create('testEntity', EmClassType.entity)
        testEntry = EmClass.create('testEntry', EmClassType.entry)
        keywords = EmType.create('keywords', testEntry)
        testEntity.link_type(keywords)

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
