import unittest

from EditorialModel.model import Model
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField

from EditorialModel.backend.json_backend import EmBackendJson
#from EditorialModel.migrationhandler.dummy import DummyMigrationHandler
from EditorialModel.migrationhandler.django import DjangoMigrationHandler

class TestModel(unittest.TestCase):

    def setUp(self):
        self.me = Model(EmBackendJson('EditorialModel/test/me.json'))

    def test_init(self):
        """ Instanciation test """
        model = Model(EmBackendJson('EditorialModel/test/me.json'))
        self.assertTrue(isinstance(model, Model))

        model = Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler=DjangoMigrationHandler('LodelTestInstance', debug=True))
        self.assertTrue(isinstance(model, Model))

    def test_components(self):
        """ Test components fetching """
        for comp_class in [EmClass, EmType, EmField, EmFieldGroup]:
            comp_l = self.me.components(comp_class)
            for component in comp_l:
                self.assertTrue(isinstance(component, comp_class), "Model.components method doesn't return EmComponent of the right type. Asked for {} but got {}".format(type(comp_class), type(component)))

    def test_sort_components(self):
        """ Test that Model.sort_components method actually sort components """
        # disordering an EmClass
        cl_l = self.me.components(EmClass)
        last_class = cl_l[0]
        last_class.rank = 10000
        self.me.sort_components(EmClass)
        self.assertEqual(self.me._components['EmClass'][-1].uid, last_class.uid, "The sort_components method doesn't really sort by rank")

    def test_new_uid(self):
        """ Test that model.new_uid return a new uniq uid """
        new_uid = self.me.new_uid()
        self.assertNotIn(new_uid, self.me._components['uids'].keys())

    def test_hash(self):
        """ Test that __hash__ and __eq__ work properly on models """
        me1 = Model(EmBackendJson('EditorialModel/test/me.json'))
        me2 = Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler=DjangoMigrationHandler('LodelTestInstance', debug=True))

        self.assertEqual(hash(me1), hash(me2), "When instanciate from the same backend & file but with another migration handler the hashes differs")
        self.assertTrue(me1.__eq__(me2))

        cl_l = me1.classes()
        cl_l[0].modify_rank(1)

        self.assertNotEqual(hash(me1), hash(me2), "After a class rank modification the hashes are the same")
        self.assertFalse(me1.__eq__(me2))

        cl_l = me2.classes()
        cl_l[0].modify_rank(1)

        self.assertEqual(hash(me1), hash(me2), "After doing sames modifications in the two models the hashes differs")
        self.assertTrue(me1.__eq__(me2))