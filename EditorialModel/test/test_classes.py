"""
    Tests for the EmClass class
"""

import os

from unittest import TestCase

from django.conf import settings
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.types import EmType
from Database.sqlsetup import SQLSetup
from Database import sqlutils
import sqlalchemy as sqla


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

## run once for this module
# define the Database for this module (an sqlite database)
def setUpModule():
    settings.LODEL2SQLWRAPPER['db']['default'] = {'ENGINE':'sqlite', 'NAME':'/tmp/testdb.sqlite'}

class ClassesTestCase(TestCase):

    # run before every instanciation of the class
    @classmethod
    def setUpClass(cls):
        sql = SQLSetup()
        sql.initDb()

    # run before every function of the class
    def setUp(self):
        pass


# creating an new EmClass should
# - create a table named like the created EmClass
# - insert a new line in em_classes
class TestEmClassCreation(ClassesTestCase):

    # create a new EmClass, then test on it
    @classmethod
    def setUpClass(cls):
        ClassesTestCase.setUpClass()
        EmClass.create('testClass', EmClassType.entity)

    # test if a table 'testClass' was created
    # should be able to select on the created table
    def test_table_em_classes(self):
        conn = sqlutils.getEngine().connect()
        a = sqlutils.meta(conn)
        try:
            newtable = sqla.Table('testClass', sqlutils.meta(conn))
            req = sqla.sql.select([newtable])
            res = conn.execute(req)
            res = res.fetchall()
            conn.close()
        except:
            self.fail("unable to select table testClass")
        self.assertEqual(res, [])

    # the uid should be 1
    def test_uid(self):
        cl = EmClass('testClass')
        self.assertEqual(cl.uid, 1)

    # the name should be the one given
    def test_classname(self):
        cl = EmClass('testClass')
        self.assertEqual(cl.name, 'testClass')

    # the classtype should have the name of the EmClassType
    def test_classtype(self):
        cl = EmClass('testClass')
        self.assertEqual(cl.classtype, EmClassType.entity['name'])

# interface to fieldGroups
class TestEmClassFieldgroups(ClassesTestCase):

    # create a new EmClass, then test on it
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        test_class = EmClass.create('testClass', EmClassType.entity)

    # test if fieldgroups() return a list of EmFieldGroup
    def test_fieldgroups(self):
        test_class = EmClass('testClass')
        fg1 = EmFieldGroup.create('fg1', test_class)
        fg2 = EmFieldGroup.create('fg2', test_class)

        fieldgroups = test_class.fieldgroups()
        self.assertIsInstance(fieldgroups, list)
        for fieldgroup in fieldgroups:
            self.assertIsInstance(fieldgroup, EmFieldGroup)

    # with no fieldgroups fieldgroups() should return an empty list
    def test_no_fieldgroups(self):
        test_class = EmClass('testClass')
        fieldgroups = test_class.fieldgroups()
        self.assertEqual(fieldgroups, [])

# interface to fieldGroups
class TestEmClassTypes(ClassesTestCase):

    # create a new EmClass, then test on it
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ClassesTestCase.setUpClass()
        test_class = EmClass.create('testClass', EmClassType.entity)

    # test if types() return a list of EmType
    def test_types(self):
        test_class = EmClass('testClass')
        t1 = EmType.create('t1', test_class)
        t2 = EmType.create('t2', test_class)

        types = test_class.types()
        self.assertIsInstance(types, list)
        for t in types:
            self.assertIsInstance(t, EmType)

    # with no type types() should return an empty list
    def test_no_types(self):
        test_class = EmClass('testClass')
        types = test_class.types()
        self.assertEqual(types, [])
