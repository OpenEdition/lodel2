import unittest

from EditorialModel.model import Model
from EditorialModel.components import EmComponent
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField

from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler


class TestEmComponent(unittest.TestCase):
    def setUp(self):
        self.me =  Model(EmBackendJson('EditorialModel/test/me.json'))
    
    def test_init(self):
        """ Testing that __init__ is abstract for an EmComponent """
        with self.assertRaises(NotImplementedError):
            foo = EmComponent(self.me, self.me.new_uid(), 'invalid instanciation')

    def test_hashes(self):
        """ Testing __hash__ and __eq__ methos """
        me1 =  Model(EmBackendJson('EditorialModel/test/me.json'))
        me2 =  Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler = DummyMigrationHandler(True))
        
        for comp_class in [EmClass, EmType, EmField, EmFieldGroup]:
            comp_l1 = me1.components(comp_class)
            comp_l2 = me2.components(comp_class)

            for i, comp1 in enumerate(comp_l1):
                comp2 = comp_l2[i]
                self.assertEqual(hash(comp1), hash(comp2), "hashes differs for two EmComponent({}) instanciated from the same backend and files".format(comp_class.__name__))
                self.assertTrue(comp1 == comp2)

                comp1.modify_rank(1)

                self.assertNotEqual(hash(comp1), hash(comp2), "hashes are the same after a modification of rank on one of the two components")
                self.assertFalse(comp1 == comp2)

                comp2.modify_rank(2)
                self.assertEqual(hash(comp1), hash(comp2), "hashes differs for two EmComponent({}) after applying the same modifications on both".format(comp_class.__name__))
                self.assertTrue(comp1 == comp2)

    def test_modify_rank(self):
        """ Testing modify_rank and set_rank method """
        cls = self.me.classes()[0]
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

        with self.assertRaises(ValueError):
            cls.modify_rank(1)

        with self.assertRaises(ValueError):
            cls.modify_rank(-10)

        with self.assertRaises(ValueError):
            cls.set_rank(0)

        with self.assertRaises(ValueError):
            cls.set_rank(10)

        with self.assertRaises(ValueError):
            cls.set_rank(-10)

    def test_check(self):
        """ Testing check method """
        cls = self.me.classes()[0]
        cls.rank = 10000

        cls.check()
        self.assertEqual(cls.rank, cls.get_max_rank())

        cls.rank = -1000
        cls.check()
        self.assertEqual(cls.rank, 1)

        
