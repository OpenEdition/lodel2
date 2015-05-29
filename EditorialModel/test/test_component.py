#from django.test import TestCase
from unittest import TestCase
from EditorialModel.component import EmComponent

class ComponentTestCase(TestCase):

    def test_component_instanciate_with_numeric_id(self):
        testComp = EmComponent(2)
        self.assertEqual(testComp.id, 2)

