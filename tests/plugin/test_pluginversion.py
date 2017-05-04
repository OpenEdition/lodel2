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

from lodel.plugin.plugins import PluginVersion
from lodel.plugin.exceptions import PluginVersionError

class PluginVersionTestCase(unittest.TestCase):

    def test_init_str(self):
        """Tests PluginVersion instanciation from string"""
        test_datas = [(1,2,3), (0,0,0), (54,0,1)]

        for test_data in test_datas:
            str_init = '.'.join([str(v) for v in test_data])
            v = PluginVersion(str_init)
            self.assertEqual(str(v), str_init)
            for i, field in enumerate(['major', 'minor', 'revision']):
                self.assertEqual(test_data[i], getattr(v, field))
    
    def test_init_short_str(self):
        """ Tests PluginVersion instanciation from string with less than
            3 numbers"""
        #Tuples with shortstr, expected result
        test_datas = [
            ("1", "1.0.0"),
            ("42", "42.0.0"),
            ("0.1", "0.1.0"),
            ("1.0", "1.0.0"),
            ("0", "0.0.0")]
        for test_str, expt_res in test_datas:
            v = PluginVersion(test_str)
            self.assertEqual(expt_res, str(v),
                "When instanctiated with '%s' expected result was '%s', but \
got : '%s'" % (test_str, expt_res, str(v)))

    def test_init_invalid_str(self):
        """Tests PluginVersion instanciation from invalid string"""
        test_datas = {
            'bad count': '1.2.3.4.5',
            'bad values': 'a.1.2',
            'bad separators': '1;2;3',
            'bad value': 'foobar' }

        for fail_reason, value in test_datas.items():
            with self.assertRaises(PluginVersionError,msg="Instanciation \
should fail when '%s' is given as argument because it is a %s" % (
    value, fail_reason)):
                v = PluginVersion(value)

    def test_comparison(self):
        """ Tests comparison operators on PluginVersion """
        cmp_funs = [
            PluginVersion.__lt__,
            PluginVersion.__le__,
            PluginVersion.__eq__,
            PluginVersion.__ne__,
            PluginVersion.__gt__,
            PluginVersion.__ge__]

        cmp_values_res = [
            (   ("0.0.0", "0.0.0"),
                (False, True, True, False, False, True)),
            (   ("1.0.0", "0.0.0"),
                (False, False, False, True, True, True)),
            (   ("0.0.0", "1.0.0"),
                (True, True, False, True, False, False)),
            (   ("3.2.1", "2.2.1"),
                (False, False, False, True, True, True)),
            (   ("3.2.1", "3.2.2"),
                (True, True, False, True, False, False)),
            (   ("3.2.1", "3.3.0"),
                (True, True, False, True, False, False)),
            (   ("3.2.2018", "3.2.1"),
                (False, False, False, True, True, True)),
            (   ("3.42.0", "3.24.520000"),
                (False, False, False, True, True, True))
        ]

        for cmp_cnt, (cmp_str_values, expt_res) in enumerate(cmp_values_res):
            cmp_values = tuple([PluginVersion(v) for v in cmp_str_values])
            for i, cmp_fun in enumerate(cmp_funs):
                if expt_res[i]:
                    self.assertTrue(cmp_fun(*cmp_values),
                        msg="Expected comparison %d %s%s to be True, but False \
returned" % (cmp_cnt, cmp_fun, cmp_values))
                else:
                    self.assertFalse(cmp_fun(*cmp_values),
                        msg="Expected comparison %d %s%s to be False, but True \
returned" % (cmp_cnt, cmp_fun, cmp_values))
                
