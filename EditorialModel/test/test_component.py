import unittest

from EditorialModel.model import Model
from EditorialModel.components import EmComponent
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField

from Lodel.utils.mlstring import MlString

from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler


class TestEmComponent(unittest.TestCase):
    def setUp(self):
        self.model = Model(EmBackendJson('EditorialModel/test/me.json'))

    def test_hashes(self):
        """ Testing __hash__ and __eq__ methods """
        me1 = Model(EmBackendJson('EditorialModel/test/me.json'))
        me2 = Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler=DummyMigrationHandler())

        for comp_class in [EmClass, EmType, EmField, EmFieldGroup]:
            comp_l1 = me1.components(comp_class)
            comp_l2 = me2.components(comp_class)

            for i, comp1 in enumerate(comp_l1):
                comp2 = comp_l2[i]
                self.assertEqual(hash(comp1), hash(comp2), "hashes differs for two EmComponent({}) instanciated from the same backend and files".format(comp_class.__name__))
                self.assertTrue(comp1 == comp2)

                if not comp1.modify_rank(1):
                    continue #modification not made, drop this test

                self.assertNotEqual(hash(comp1), hash(comp2), "hashes are the same after a modification of rank on one of the two components")
                self.assertFalse(comp1 == comp2)

                comp2.modify_rank(1)

                self.assertEqual(hash(comp1), hash(comp2), "hashes differs for two EmComponent({}) after applying the same modifications on both".format(comp_class.__name__))
                self.assertTrue(comp1 == comp2)

    def test_virtual_methods(self):
        """ Testing virtual methods """
        with self.assertRaises(NotImplementedError):
            _ = EmComponent(self.model, self.model.new_uid(), 'Invalide')

    def test_modify_rank(self):
        """ Testing modify_rank and set_rank method """
        cls = self.model.classes()[0]
        orig_rank = cls.rank

        cls.modify_rank(1)
        self.assertEqual(orig_rank, cls.rank - 1)

        cls.modify_rank(-1)
        self.assertEqual(orig_rank, cls.rank)

        cls.set_rank(1)
        self.assertEqual(cls.rank, 1)

        cls.set_rank(2)
        self.assertEqual(cls.rank, 2)

        max_rank = cls.get_max_rank()
        cls.set_rank(max_rank)
        self.assertEqual(cls.rank, max_rank)

        self.assertFalse(cls.modify_rank(1))

        self.assertFalse(cls.modify_rank(-10))

        with self.assertRaises(ValueError):
            cls.set_rank(0)

        with self.assertRaises(ValueError):
            cls.set_rank(10)

        with self.assertRaises(ValueError):
            cls.set_rank(-10)

    def test_check(self):
        """ Testing check method """
        cls = self.model.classes()[0]
        cls.rank = 10000

        cls.check()
        self.assertEqual(cls.rank, cls.get_max_rank())

        cls.rank = -1000
        cls.check()
        self.assertEqual(cls.rank, 1)

    def test_dump(self):
        """ Testing dump methods """
        for comp in self.model.components():
            dmp = comp.attr_dump()
            self.assertNotIn('uid', dmp)
            self.assertNotIn('model', dmp)
            self.assertTrue(dmp['help_text'] is None or isinstance(dmp['help_text'], MlString))
            self.assertTrue(dmp['string'] is None or isinstance(dmp['string'], MlString))
            for dmp_f in dmp:
                self.assertFalse(dmp_f.startswith('_'))

    def test_uniq_name(self):
        """ Testing uniq_name method """
        names_l = []
        for comp in self.model.components():
            #Should be uniq only for types and classes
            if isinstance(comp, EmType) or isinstance(comp, EmClass):
                self.assertNotIn(comp.uniq_name, names_l)
                names_l.append(comp.uniq_name)
