from django.test import TestCase
from EditorialModel.lib.component import EmComponent

class ComponentTestCase(TestCase):
    def setup(self):
        testComp = EmComponent(2)

    def component_instanciate_with_numeric_id(self):
        self.assertEqual(testComp.id, 2)
