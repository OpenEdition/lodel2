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


import copy
import datetime
import unittest
from unittest import mock
from unittest.mock import patch

import tests.loader_utils
from tests.leapi.query.utils import dyncode_module as dyncode
from lodel.leapi.query import LeDeleteQuery, LeUpdateQuery, LeGetQuery, \
    LeInsertQuery
from lodel.leapi.exceptions import *

class LeQueryDatasourceTestCase(unittest.TestCase):
    """ Testing LeQuery objects connection with datasource """

    mockread = mock.MagicMock()
    mockwrite = mock.MagicMock()
    dyncode = None

    @classmethod
    def setUpClass(cls):
        """ Mocking read & write datasource of dyncode """
        cls.dyncode = dict()
        for dyncls in dyncode.dynclasses:
            dyncls._ro_datasource = cls.mockread
            dyncls._rw_datasource = cls.mockwrite
            cls.dyncode[dyncls.__name__] = dyncls

    def setUp(self):
        """ Reseting all mock calls before test """
        self.mockread.reset_mock()
        self.mockwrite.reset_mock()

    def check_nocall(self, read = True, exclude = None):
        """ Utility function to check if a datasource mock method has been
            called during test """
        exclude = [] if exclude is None else exclude
        if read:
            mockds = self.mockread
        else:
            mockds = self.mockwrite

        if 'select' not in exclude:
            self.assertFalse(
                mockds.select.called,
                "select method was not expected to be called")
        if 'delete' not in exclude:
            self.assertFalse(
                mockds.delete.called,
                "delete method was not expected to be called")
        if 'update' not in exclude:
            self.assertFalse(
                mockds.update.called,
                "update method was not expected to be called")
        if 'insert' not in exclude:
            self.assertFalse(
                mockds.insert.called,
                "insert method was not expected to be called")

    def test_delete_simple_filter(self):
        """ Testing delete query mocking datasource using simple query
            filters """
        cls = self.dyncode['Person']
        query = LeDeleteQuery(
            target_class = cls,
            query_filter = ['lodel_id = 1', 'alias.lodel_id = 2'])
        query.execute()
        # Cannot check with assert_called_once_with because of the array
        # that is not in a deterministic order
        call_args = self.mockwrite.delete.call_args[0]
        self.assertEqual(call_args[0], cls)
        self.assertEqual(
            sorted(call_args[1]),
            sorted([('lodel_id', '=', 1), ('alias', '=', '2')]))
        self.assertEqual(call_args[2], [])
        self.check_nocall(read = False, exclude = ['delete'])
        self.check_nocall(read = True)


    def test_delete_simple_rel_filters(self):
        """ Testing delete query mocking datasource using simple filters
            and relationnal filters"""
        cls = self.dyncode['Person']
        query = LeDeleteQuery(
            target_class = cls,
            query_filter = ['lodel_id = 1', 'alias.firstname = foo'])
        query.execute()
        self.mockwrite.delete.assert_called_once_with(
            cls,
            [('lodel_id', '=', 1)],
            [(('alias', {cls: 'firstname'}), '=', 'foo')])
        self.check_nocall(read = False, exclude = ['delete'])
        self.check_nocall(read = True)

    def test_delete_rel_filters(self):
        """ Testing delete query mocking datasource """
        cls = self.dyncode['Person']
        query = LeDeleteQuery(
            target_class = cls,
            query_filter = ['alias.firstname = foo'])
        query.execute()
        self.mockwrite.delete.assert_called_once_with(
            cls,
            [],
            [(('alias', {cls: 'firstname'}), '=', 'foo')])
        self.check_nocall(read = False, exclude = ['delete'])
        self.check_nocall(read = True)

    @unittest.skip("Waiting references checks stack implementation")
    def test_insert(self):
        """ Testing LeInsertQuery mocking datasource """
        cls = self.dyncode['Person']
        query = LeInsertQuery(
            target_class = cls)
        self.mockwrite.insert.return_value = 1
        datas = {
            'firstname': 'foo',
            'lastname': 'bar',
            'alias': None}
        query.execute(datas)
        self.assertEqual(self.mockwrite.insert.call_count, 1)
        cargs , _ = self.mockwrite.insert.call_args
        pdatas = cls.prepare_datas(datas, True, False)
        self.assertEqual(cargs[0], cls)
        cargs = cargs[1]
        self.assertEqual(set(pdatas.keys()), set(cargs.keys()))
        for dname in pdatas:
            if isinstance(pdatas[dname], datetime.datetime):
                d1 = pdatas[dname]
                d2 = cargs[dname]
                for vname in ('year', 'month', 'day', 'hour', 'minute'):
                    self.assertEqual(
                        getattr(d1, vname), getattr(d2, vname))
                pass
            else:
                self.assertEqual(pdatas[dname], cargs[dname])
        self.check_nocall(read = False, exclude = ['insert'])
        self.check_nocall(read = True)

    def test_update_instance(self):
        """ Testing LeUpdateQuery with an instance mocking datasource """
        cls = self.dyncode['Person']
        inst = cls(lodel_id = 1, firstname = 'foo', lastname = 'bar',
            alias = None, linked_texts = None)
        query = LeUpdateQuery(inst)

        with self.assertRaises(LeApiQueryError):
            # Bad call, giving data while an instance was given to __init__
            query.execute(data = {'firstname': 'ooba'})

        query.execute()
        self.mockwrite.update.assert_called_once_with(
            cls,
            [('lodel_id', '=', '1')],
            [],
            inst.datas(True))
        self.check_nocall(read=False, exclude = ['update'])
        self.check_nocall(read=True)

    def test_update_filter(self):
        """ Testing LeUpdateQuery with filter mocking datasource """
        cls = self.dyncode['Person']
        fake_db_datas = [{
            'lodel_id': 1,
            'firstname': 'barfoo',
            'lastname': 'foobar',
            'fullname': 'barfoo foobar',
            'alias': None,
            'linked_texts': None,
            'help_text': None,
            'classname': 'Person',
            'date_create': None,
            'date_update': None}]
        q_datas = {'firstname': 'foobar', 'lastname': 'barfoo'}

        expt_datas = copy.copy(fake_db_datas[0])
        expt_datas.update(q_datas)
        expt_datas = cls.prepare_datas(expt_datas, True, True)

        query = LeUpdateQuery(cls, [('lodel_id', '=', 1)])
        with self.assertRaises(LeApiQueryError):
            # Bad call, no datas given while a class and a filters were given
            # to __init__
            query.execute()
        self.mockread.select.return_value = fake_db_datas
        query.execute(q_datas)
        self.mockwrite.update.asser_called_once_with(
            cls,
            [('lodel_id', '=', '1')],
            [],
            expt_datas)
