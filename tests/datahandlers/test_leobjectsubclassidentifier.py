import unittest
from unittest import mock 
from unittest.mock import patch

import leapi_dyncode as dyncode

from lodel.leapi.datahandlers.datas import LeobjectSubclassIdentifier
from lodel.plugins.dummy_datasource.datasource import DummyDatasource


class LeobjectSubclassIdentifierTestCase(unittest.TestCase):
    
    def test_throws_error_if_not_internal(self):
        self.failUnlessRaises(RuntimeError, LeobjectSubclassIdentifier, internal=False)
        
