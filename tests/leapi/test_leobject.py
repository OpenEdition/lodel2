import unittest
from unittest import mock
from unittest.mock import patch

import tests.loader_utils
from tests.leapi.query.utils import dyncode_module as dyncode

from lodel.leapi.leobject import LeObject
from lodel.leapi.query import LeDeleteQuery, LeUpdateQuery, LeGetQuery, \
    LeInsertQuery
from lodel.leapi.exceptions import *

class LeObjectDummyTestCase(unittest.TestCase):
    """ Testing LeObject method with a dummy datasource """

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
        with self.assertRaises(LeApiError):
            dyncode.Person(lastname = "foo", firstname = "bar")

    def test_data_accessor(self):
        """ Testing data accessor method """
        inst = dyncode.Person(lodel_id = 1, lastname = "foo")
        self.assertEqual(inst.data('lodel_id'), 1)
        self.assertEqual(inst.data('lastname'), 'foo')

    def test_data_accessor_fails(self):
        """ Testing that data accessor detects unitialized fields """
        inst = dyncode.Person(lodel_id = 1, lastname = "foo")
        with self.assertRaises(RuntimeError):
            inst.data('firstname')

    def test_name2class(self):
        """ Testing the class method that returns a dynamic object given it's
            name """
        self.assertEqual(dyncode.Object.name2class('Person'), dyncode.Person)
        self.assertEqual(dyncode.Object.name2class('Object'), dyncode.Object)
    
    def test_bad_name2class(self):
        """ Testing failures of the class method that returns a dynamic object
            given it's name """
        badnames = ['foobar', 'str', str, None, 42]
        callers = [dyncode.Object, dyncode.Person, dyncode.Entitie]
        for caller in callers:
            for badname in badnames:
                with self.assertRaises(LeApiError, msg="LeApiError not raised \
but invalid name %s was given" % badname):
                    caller.name2class(badname)

    def test_abstract_name2class(self):
        with self.assertRaises(NotImplementedError):
            LeObject.name2class('Person')
        with self.assertRaises(NotImplementedError):
            LeObject.name2class(42)

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
        """ Testing insert method """
        dyncode.Person.insert({'lastname': 'foo', 'firstname': 'bar'})
    
    def test_bad_insert(self):
        """ Insert with bad arguments """
        badargs = [
            {},
            {'lodel_id': 1,'lastname': 'foo', 'firstname': 'bar'}]
        
        for arg in badargs:
            with self.assertRaises(LeApiDataCheckErrors):
                dyncode.Person.insert(arg)

    def test_delete_instance(self):
        """ Testing instance method delete """
        inst = dyncode.Person(
            lodel_id = 1, firstname = "foo", lastname = "bar")
        inst.delete()


class LeObjectQueryMockTestCase(unittest.TestCase):
    """ Testing LeObject mocking LeQuery objects """

    def test_insert(self):
        """ Checking that LeObject insert method calls LeInsertQuery
            correctly """
        datas = {'lastname': 'foo', 'firstname': 'bar'}
        with patch.object(
            LeInsertQuery, '__init__', return_value = None) as mock_init:

            try:
                dyncode.Person.insert(datas)
            except AttributeError:
                pass #Because of mock
            mock_init.assert_called_once_with(dyncode.Person)

        with patch.object(
            LeInsertQuery, 'execute', return_value = 42) as mock_insert:

            ret = dyncode.Person.insert(datas)
            self.assertEqual(ret, 42, 'Bad return value forwarding')
            mock_insert.assert_called_once_with(datas)
    
    def test_delete(self):
        """ Checking that LeObject delete method calls LeDeleteQuery
            correctly """
        with patch.object(
            LeDeleteQuery, '__init__', return_value = None) as mock_init:

            inst = dyncode.Person(
                lodel_id = 1, firstname = "foo", lastname = "bar")
            try:
                inst.delete()
            except AttributeError:
                pass
            mock_init.assert_called_once_with(
                dyncode.Person, [('lodel_id', '=', 1)])

        with patch.object(
            LeDeleteQuery, 'execute', return_value = 1) as mock_execute:

            inst = dyncode.Person(
                lodel_id = 1, firstname = "foo", lastname = "bar")
            ret = inst.delete()
            self.assertEqual(ret, 1, 'Bad return value forwarding')
            mock_execute.assert_called_once_with(
                dyncode.Person, [('lodel_id', '=', 1)], [])

    def test_delete_bundle(self):
        """ Checking that LeObject delete_bundle method calls LeDeleteQuery
            correctly """
        with patch.object(
            LeDeleteQuery, '__init__', return_value = None) as mock_init:
            
            try:
                dyncode.Person.delete_bundle(['lodel_id > 1'])
            except AttributeError:
                pass
            mock_init.assert_called_once_with(
                dyncode.Person, ['lodel_id > 1'])

        with patch.object(
            LeDeleteQuery, 'execute', return_value = None) as mock_execute:
            
            dyncode.Person.delete_bundle(['lodel_id > 1'])
            mock_init.assert_called_once_with(
                dyncode.Person, [('lodel_id', '>', 1)], [])

