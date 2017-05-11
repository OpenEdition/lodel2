import unittest
import inspect

from lodel.leapi.datahandlers.data import LeobjectSubclassIdentifier as Testee


class LeresultectSubclassIdentifierTestCase(unittest.TestCase):        
        
        
    def test_base_type_is_varchar(self):
        self.assertEqual(Testee.base_type, 'varchar')
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(Testee.help), str)
        
    
    def test_throws_error_if_set_as_external(self):
        self.assertRaises(RuntimeError, Testee, internal=False)
        
    
    def test_set_as_internal_by_default(self):
        self.assertTrue(Testee().internal)
        
        
    def test_passing_class_returns_class_name(self):
        result = Testee.construct_data(None, object, None, None, None)
        
        self.assertEqual(result, object.__name__)
        
        
    def test_passing_instance_returns_class_name(self):
        result = Testee.construct_data(None,  object(), None, None, None)
        
        self.assertTrue(result, object.__name__)
        
        
    def test_passing_instance_and_class_same_result(self):
        objResult = Testee.construct_data(None, Testee(), None, None, None)
        clsResult = Testee.construct_data(None, Testee, None, None, None)
        
        self.assertEqual(objResult, clsResult)