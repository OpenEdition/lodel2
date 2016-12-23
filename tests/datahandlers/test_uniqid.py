import unittest
from unittest import mock 
from unittest.mock import patch

import leapi_dyncode as dyncode

from lodel.leapi.datahandlers.datas import UniqID as Testee
from lodel.plugins.dummy_datasource.datasource import DummyDatasource


class UniqIDTestCase(unittest.TestCase):
        
        
    def test_has_base_type_property(self):
        self.assertTrue(hasattr(Testee, 'base_type'))
        
        
    def test_base_type_is_int(self):
        self.assertEqual(Testee.base_type, 'int')
        
        
    def test_has_help_property(self):
        self.assertTrue(hasattr(Testee, 'help'))
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(Testee.help), str)
        
        
    def test_internal_set_as_automatic_by_default(self):
        self.assertEqual(Testee().internal, 'automatic')
        
    
    def test_construct_data_sets_new_uid_if_none(self):
        sent_uid = None
        mocked_returned_uid = 987654321
        
        with patch.object(DummyDatasource, 'new_numeric_id', return_value=mocked_returned_uid) as mock_method:
            returned_uid = Testee.construct_data(None, dyncode.Object, None, None, sent_uid)
            
            mock_method.assert_called_once_with(dyncode.Object)
            self.assertEqual(returned_uid, mocked_returned_uid)
            

    def test_construct_data_returns_already_set_uid(self):
        sent_uid = 123456789
        mocked_returned_uid = 987654321
        
        with patch.object(DummyDatasource, 'new_numeric_id', return_value=mocked_returned_uid) as mock_method:
            returned_uid = Testee.construct_data(None, dyncode.Object, None, None, sent_uid)

            self.assertEqual(returned_uid, sent_uid)
            mock_method.assert_not_called()     