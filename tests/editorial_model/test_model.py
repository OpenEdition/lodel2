#-*- coding: utf-8 -*-

import unittest

from lodel.editorial_model.components import EmComponent, EmClass, EmField, EmGroup
from lodel.utils.mlstring import MlString
from lodel.editorial_model.exceptions import *

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
        cls.new_field('name', data_handler = None)
        cls.new_field('string', data_handler = None)
        cls.new_field('lodel_id', data_handler = None)

        fields = cls.fields()
        self.assertEqual(len(fields), 3)
        self.assertEqual(
            set([f.uid for f in fields]),
            set(['name', 'string', 'lodel_id'])
        )

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
