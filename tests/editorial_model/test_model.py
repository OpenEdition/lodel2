#-*- coding: utf-8 -*-

import unittest

from lodel.editorial_model.model import EditorialModel
from lodel.editorial_model.components import EmComponent, EmClass, EmField, EmGroup
from lodel.utils.mlstring import MlString
from lodel.editorial_model.exceptions import *

class EditorialModelTestCase(unittest.TestCase):
    
    def test_d_hash(self):
        """ Test the deterministic hash method """
        model = EditorialModel("test model", description = "Test EM")
        cls1 = model.new_class('testclass1', display_name = 'Classe de test 1', help_text = 'super aide')
        c1f1 = cls1.new_field('c1testfield1', data_handler = 'varchar')
        c1f2 = cls1.new_field('c1testfield2', data_handler = 'varchar')
        cls2 = model.new_class('testclass2')
        c2f1 = cls2.new_field('c2testfield1', data_handler = 'varchar')
        c2f2 = cls2.new_field('c2testfield2', data_handler = 'varchar')
        grp1 = model.new_group('testgroup1')
        grp1.add_components((cls1, c1f1))
        grp2 = model.new_group('testgroup2')
        grp2.add_components((cls2, c1f2, c2f1, c2f2))
        grp2.add_dependencie(grp1)
        e_hash = 105398984207109703509695004279282115094
        self.assertEqual(model.d_hash(), e_hash)

        c2f1.uid = 'foobar'
        self.assertNotEqual(model.d_hash(), e_hash)

        c2f1.uid = 'c2testfield1'
        self.assertEqual(model.d_hash(), e_hash)


class EmComponentTestCase(unittest.TestCase):
    
    def test_abstract_init(self):
        with self.assertRaises(NotImplementedError):
            EmComponent('test')


class EmClassTestCase(unittest.TestCase):

    def test_init(self):
        cls = EmClass('testClass', 'test class', 'A test class')
        self.assertEqual(cls.uid, 'testClass')
        self.assertEqual(cls.display_name, MlString('test class'))
        self.assertEqual(cls.help_text, MlString('A test class'))

    def test_fields(self):
        """ Bad test on add field method (only check uid presence) """
        cls = EmClass('testClass', 'test_class', 'A test class')
        cls.new_field('name', data_handler = 'varchar')
        cls.new_field('string', data_handler = 'varchar')
        cls.new_field('lodel_id', data_handler = 'varchar')

        fields = cls.fields()
        self.assertEqual(len(fields), 3)
        self.assertEqual(
            set([f.uid for f in fields]),
            set(['name', 'string', 'lodel_id'])
        )

    def test_d_hash(self):
        """ Test the deterministic hash method """
        field = EmField('test field', 'foobar')
        e_hash = 16085043663725855508634914630594968402
        self.assertEqual(field.d_hash(), e_hash)
        field.uid = 'test field.'
        self.assertNotEqual(field.d_hash(), e_hash)

class EmGroupTestCase(unittest.TestCase):
    
    def test_init(self):
        """ Test EmGroup instanciation """
        grp = EmGroup('testgrp', display_name = "Test group", help_text="No Help")
        self.assertEqual(grp.uid, 'testgrp')
        self.assertEqual(grp.dependencies(), dict())
        self.assertEqual(grp.display_name, MlString("Test group"))
        self.assertEqual(grp.help_text, MlString("No Help"))
        
        grp2 = EmGroup('test')
        self.assertEqual(grp2.uid, 'test')
        self.assertEqual(grp2.display_name, None)
        self.assertEqual(grp2.help_text, None)

        grp3 = EmGroup('depends', depends = (grp, grp2))
        self.assertEqual(set(grp3.dependencies().values()), set((grp, grp2)))

    def test_deps(self):
        """ Test dependencies """
        grp1 = EmGroup('grp1')
        grp2 = EmGroup('grp2')
        grp3 = EmGroup('grp3')
        grp4 = EmGroup('grp4')

        grp2.add_dependencie(grp1)
        grp3.add_dependencie(grp2)
        grp4.add_dependencie(grp2)
        grp4.add_dependencie(grp1)

        self.assertEqual(set(grp1.dependencies().values()), set())
        self.assertEqual(set(grp2.dependencies().values()), set([grp1]))
        self.assertEqual(set(grp3.dependencies().values()), set([grp2]))
        self.assertEqual(set(grp4.dependencies().values()), set([grp2, grp1]))

        self.assertEqual(set(grp3.dependencies(True).values()), set([grp2, grp1]))
        self.assertEqual(set(grp4.dependencies(True).values()), set([grp2, grp1]))

        self.assertEqual(set(grp1.required_by.values()), set([grp2, grp4]))
        self.assertEqual(set(grp2.required_by.values()), set([grp3, grp4]))
        self.assertEqual(set(grp3.required_by.values()), set())
        self.assertEqual(set(grp4.required_by.values()), set())

        for grp in [grp1, grp2, grp3, grp4]:
            for uid, dep in grp.dependencies(recursive = True).items():
                self.assertEqual(uid, dep.uid)
            for uid, dep in grp.required_by.items():
                self.assertEqual(uid, dep.uid)
    def test_deps_complex(self):
        """ More complex dependencies handling test """
        grps = [ EmGroup('group%d' % i) for i in range(6) ]
        grps[5].add_dependencie( (grps[1], grps[2], grps[4]) )
        grps[4].add_dependencie( (grps[1], grps[3]) )
        grps[3].add_dependencie( (grps[0],) )
        grps[1].add_dependencie( (grps[2], grps[0]) )
        self.assertEqual(
                            set(grps[5].dependencies(True).values()),
                            set( grps[i] for i in range(5))
        )
        self.assertEqual(
                            set(grps[4].dependencies(True).values()),
                            set( grps[i] for i in range(4))
        )
        grps[2].add_dependencie(grps[0])
        self.assertEqual(
                            set(grps[5].dependencies(True).values()),
                            set( grps[i] for i in range(5))
        )
        self.assertEqual(
                            set(grps[4].dependencies(True).values()),
                            set( grps[i] for i in range(4))
        )
        # Inserting circular deps
        with self.assertRaises(EditorialModelError):
            grps[0].add_dependencie(grps[5])

    def test_circular_dep(self):
        """ Test circular dependencies detection """
        grps = [ EmGroup('group%d' % i) for i in range(10) ]
        for i in range(1,10):
            grps[i].add_dependencie(grps[i-1])

        for i in range(1,10):
            for j in range(i+1,10):
                with self.assertRaises(EditorialModelError):
                    grps[i].add_dependencie(grps[j])

    def test_d_hash(self):
        """ Test the deterministic hash method """
        grp = EmGroup('testgrp', display_name = "Test group", help_text="No Help")
        self.assertEqual(grp.d_hash(), 2280847427800301892840867965375148376323815160723628142616247375345365409972670566216414157235977332113867542043807295933781561540623070667142779076339712861412992217365501372435232184530261327450635383095)

