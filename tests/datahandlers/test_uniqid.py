import unittest
from unittest import mock 
from unittest.mock import patch

import leapi_dyncode as dyncode

from lodel.leapi.datahandlers.datas import UniqID
from lodel.plugins.dummy_datasource.datasource import DummyDatasource


class UniqIDTestCase(unittest.TestCase):
    
    def test_construct_data_sets_new_uid_if_none(self):
        sent_uid = None
        mocked_returned_uid = 987654321
        
        with patch.object(DummyDatasource, 'new_numeric_id', return_value=mocked_returned_uid) as mock_method:
            returned_uid = UniqID.construct_data(UniqID, dyncode.Object, 'lodel_id', '', sent_uid)
            
            mock_method.assert_called_once_with(dyncode.Object)
            self.assertEqual(returned_uid, mocked_returned_uid)
            
    def test_construct_data_returns_already_set_uid(self):
        sent_uid = 123456789
        mocked_returned_uid = 987654321
        
        with patch.object(DummyDatasource, 'new_numeric_id', return_value=mocked_returned_uid) as mock_method:
            returned_uid = UniqID.construct_data(UniqID, dyncode.Object, '', '', sent_uid)

            self.assertEqual(returned_uid, sent_uid)
            mock_method.assert_not_called()     
        