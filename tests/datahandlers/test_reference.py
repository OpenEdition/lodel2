# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#



import unittest

from lodel.leapi.datahandlers.base_classes import Reference, MultipleRef
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


class MultipleRefTestCase(unittest.TestCase):

    def test_multiref_check_data_value_not_iter(self):
        test_multiref = MultipleRef(3)
        for test_value in [obj3]:
            with self.assertRaises(FieldValidationError):
                test_multiref._check_data_value(test_value)
    
    def test_multiref_check_data_multi_bad_value_error(self):
        test_multiref = MultipleRef(3)
        for test_value in [(obj3, 15, 'toto')]:
            with self.assertRaises(FieldValidationError) as cm:
                test_multiref._check_data_value(test_value)
            the_exception = cm.exception
            self.assertEqual(the_exception.args, ("MultipleRef have for invalid values [15,'toto']  :",))
    
    def test_multiref_check_data_too_max_lenght_iter_error(self):
        test_multiref = MultipleRef(3)
        for test_value in [(obj3, obj2, obj1, obj3)]:
            with self.assertRaises(FieldValidationError):
                test_multiref._check_data_value(test_value)


    def test_multiref_check_data_uid_multi_bad_value_error(self):
        test_multiref = MultipleRef(5, **{'allowed_classes' : [dyncode.Person, dyncode.Collection]})
        for test_value in [(obj3, obj2, 1, 15, 'toto')]:
            with self.assertRaises(FieldValidationError) as cm:
                test_multiref._check_data_value(test_value)
            the_exception = cm.exception
            self.assertEqual(the_exception.args, ("MultipleRef have for invalid values ['toto']  :",))
    
    def test_multiref_check_data_object_uid_multi_good_value_error(self):
        test_multiref = MultipleRef(5, **{'allowed_classes' : [dyncode.Person, dyncode.Collection]})
        for test_value in [(obj3, obj2, 1.2, 15)]:
                value = test_multiref._check_data_value(test_value)
                self.assertEqual(value, [obj3, obj2, 1, 15])
