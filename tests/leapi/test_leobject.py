import unittest

import tests.loader_utils
from tests.leapi.query.utils import dyncode_module as dyncode

from lodel.leapi.leobject import LeApiDataCheckError
from lodel.leapi.query import LeDeleteQuery, LeUpdateQuery, LeGetQuery
from lodel.leapi.exceptions import *

class LeFilteredQueryTestCase(unittest.TestCase):

    q_classes = [ LeDeleteQuery, LeUpdateQuery, LeGetQuery ]

    def test_init(self):
        """ Testing LeObject child class __init__ """
        dyncode.Person(
            lodel_id = '1',
            lastname = "Foo",
            firstname = "Bar",
            alias = "Foobar")

    def test_init_abstract(self):
        """ Testing init abstract LeObject childs """
        abstract_classes = [
            dyncode.Entitie, dyncode.Indexabs]
        for cls in abstract_classes:
            with self.assertRaises(NotImplementedError):
                cls(lodel_id = 1)

    def test_init_bad_fields(self):
        """ Testing init with bad arguments """
        with self.assertRaises(LeApiErrors):
            dyncode.Person(
                lodel_id = 1,
                foobar = "barfoo")
        with self.assertRaises(LeApiErrors):
            dyncode.Person(lastname = "foo", firstname = "bar")

    
    def test_initilized(self):
        """ Testing initialized method """
        inst = dyncode.Person(
            lodel_id = 1, lastname="foo")
        self.assertFalse(inst.initialized)

    def test_uid_fieldname(self):
        self.assertEqual(dyncode.Person.uid_fieldname(), ["lodel_id"])

    def test_fieldnames_accessor(self):
        """ Testing fieldnames() accessor method """
        fnames = dyncode.Person.fieldnames(False)
        self.assertEqual(set(fnames),
            {'lastname', 'linked_texts', 'firstname', 'alias'})

    def test_insert(self):
        dyncode.Person.insert({'lastname': 'foo', 'firstname': 'bar'})
    
    @unittest.skip("wait")
    def test_bad_insert(self):
        """ Insert with bad arguments """
        dyncode.Person.insert({})
        dyncode.Person.insert({'lodel_id': 1,'lastname': 'foo', 'firstname': 'bar'})

