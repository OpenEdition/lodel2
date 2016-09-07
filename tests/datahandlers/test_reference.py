
import unittest

from lodel.leapi.datahandlers.base_classes import Reference
from leapi.query.utils import init_dyncode
from lodel.exceptions import *
from lodel.leapi.leobject import LeObject

dyncode = init_dyncode()
obj1 = dyncode.Person(
lodel_id = '1',
lastname = "Foo",
firstname = "Bar",
alias = "Foobar")

obj2 = dyncode.Collection(
lodel_id = '3',
title = "Foo)")

obj3 = dyncode.Collection(
lodel_id = '4',
title = "Foo")

class ReferenceTestCase(unittest.TestCase):

    def test_init_reference_class(self):
        reference = None
        try:
            reference = Reference()
        except NotImplementedError:
            self.assertNotIsInstance(reference, DataHandler)
            self.assertIsNone(datahandler)

    def test_reference_check_bad_data_value(self):
        test_ref = Reference((obj1, obj2))
        for test_value in ['toto']:
            with self.assertRaises(FieldValidationError):
                test_ref._check_data_value(test_value)

    def test_reference_check_good_data_value(self):
        test_ref = Reference((obj1,))
        for test_value in [obj3, 15]:
            value = test_ref._check_data_value(test_value)
            self.assertEqual(test_value, value)


class MultipleRefTestCase(unnittest.case):

    def test_multiref_check_data_value_not_iter(self):
        multiref = MultipleRef(3)
        for test_value in [obj3, 15]:
            value = test_ref._check_data_value(test_value)
            self.assertEqual(test_value, value)

