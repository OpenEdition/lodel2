#-*- coding: utf-8 -*-

import unittest

import tests.loader_utils
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
        e_hash = 0x250eab75e782e51bbf212f47c6159571
        self.assertEqual(model.d_hash(), e_hash)

        c2f1.uid = 'foobar'
        self.assertNotEqual(model.d_hash(), e_hash)

        c2f1.uid = 'c2testfield1'
        self.assertEqual(model.d_hash(), e_hash)

    def test_translator_from_name(self):
        """ Test the translator_from_name method """
        import lodel.editorial_model.translator.picklefile as expected
        translator = EditorialModel.translator_from_name('picklefile')
        self.assertEqual(translator, expected)

    def test_invalid_translator_from_name(self):
        """ Test the translator_from_name method when invalid names given as argument """
        import lodel.editorial_model.translator.picklefile
        invalid_names = [
            lodel.editorial_model.translator.picklefile,
            'foobar',
            42,
        ]

        for name in invalid_names:
            with self.assertRaises(NameError):
                EditorialModel.translator_from_name(name)


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
        field = EmField('test field', 'varchar')
        e_hash = 0x23415e5cab5cabf29ab2d2db99998ba4
        self.assertEqual(field.d_hash(), e_hash)
        field.uid = 'test field.'
        self.assertNotEqual(field.d_hash(), e_hash)

    def test_field_override(self):
        """ Test EmClass field overriding in inheritance """
        cls1 = EmClass('testClass', 'test class')
        cls1.new_field('test', data_handler = 'varchar', max_length = 16, nullable=True)
        cls1.new_field('test2', data_handler = 'integer', nullable = True)

        cls2 = EmClass('testClass2', parents = cls1)
        cls2.new_field('test', data_handler = 'varchar', max_length = 16, nullable=False)
        cls2.new_field('test2', data_handler = 'integer', nullable = False)

        self.assertEqual(len(cls1.fields()), len(cls2.fields()))
        self.assertTrue(cls1.fields('test').data_handler_options['nullable'])
        self.assertFalse(cls2.fields('test').data_handler_options['nullable'])

    ## @todo add more test when data handlers implements compatibility checks
    def test_field_invalid_type_override(self):
        """ Testing invalid fields overriding (incompatible data_handler)"""
        cls1 = EmClass('testClass', 'test class')
        cls1.new_field('test', data_handler = 'varchar', max_length = 8)
        cls1.new_field('test2', data_handler = 'integer', nullable = True)

        cls2 = EmClass('testClass2', parents = cls1)
        with self.assertRaises(AttributeError):
            cls2.new_field('test', data_handler = 'integer')

    def test_field_invalid_options_overrid(self):
        """ Testing invalid fields overriding (incompatible data handler options) """
        cls1 = EmClass('testClass', 'test class')
        cls1.new_field('test', data_handler = 'varchar', max_length = 8)
        cls1.new_field('test2', data_handler = 'integer', nullable = True)

        cls2 = EmClass('testClass2', parents = cls1)
        with self.assertRaises(AttributeError):
            cls2.new_field('test', data_handler = 'varchar', max_length = 2)

    def test_parents_recc(self):
        """ Test the reccursive parents property """
        model = EditorialModel(
                                    "test_model",
                                    description = "Model for LeFactoryTestCase"
        )
        cls1 = model.new_class('testclass1')
        cls2 = model.new_class('testclass2')
        cls3 = model.new_class('testclass3', parents = [cls2])
        cls4 = model.new_class('testclass4', parents = [cls1, cls3])
        cls5 = model.new_class('testclass5', parents = [cls4])
        cls6 = model.new_class('testclass6')

        self.assertEqual(cls5.parents_recc, set((cls4, cls1, cls2, cls3)))
        self.assertEqual(cls1.parents_recc, set())
        self.assertEqual(cls4.parents_recc, set((cls1, cls2, cls3)))
        self.assertEqual(cls3.parents_recc, set((cls2,)))

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
        
    def test_add_comps(self):
        """ Test components adding in groups"""
        grp = EmGroup('grp')
        cpn1 = EmField('test1','integer')
        cpn2 = EmClass('testClass', 'test class')
        grp.add_components([cpn1,cpn2])
        
        s1=grp.components()
        s2=grp.components()
        s1.add(EmField('test2','varchar'))
        self.assertEqual(s2,set([cpn1,cpn2]));

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
                
    def test_apps(self):
        """ Test applicants """
        grp1 = EmGroup('grp1')
        grp2 = EmGroup('grp2')
        grp3 = EmGroup('grp3')
        grp4 = EmGroup('grp4')

        grp2.add_applicant(grp1)
        grp3.add_applicant(grp2)
        grp4.add_applicant(grp2)
        grp4.add_applicant(grp1)

        self.assertEqual(set(grp1.applicants().values()), set())
        self.assertEqual(set(grp2.applicants().values()), set([grp1]))
        self.assertEqual(set(grp3.applicants().values()), set([grp2]))
        self.assertEqual(set(grp4.applicants().values()), set([grp2, grp1]))

        self.assertEqual(set(grp3.applicants(True).values()), set([grp2, grp1]))
        self.assertEqual(set(grp4.applicants(True).values()), set([grp2, grp1]))

        self.assertEqual(set(grp1.required_by.values()), set())
        self.assertEqual(set(grp2.required_by.values()), set([grp1]))
        self.assertEqual(set(grp3.required_by.values()), set([grp2]))
        self.assertEqual(set(grp4.required_by.values()), set([grp2,grp1]))

        for grp in [grp1, grp2, grp3, grp4]:
            for uid, dep in grp.applicants(recursive = True).items():
                self.assertEqual(uid, dep.uid)
            for uid, dep in grp.required_by.items():
                self.assertEqual(uid, dep.uid)
                
    def test_display_name(self):
        grp = EmGroup('grp',None,'Test affichage du nom')
        a = grp.get_display_name()
        b = a
        b = 'Test de copie du nom'
        self.assertEqual(a,'Test affichage du nom')
        grp1 = EmGroup('grp')
        c = grp1.get_display_name()
        self.assertEqual(c, None)
        with self.assertRaises(ValueError): grp.get_display_name('ita')
        
    def test_help_text(self):
        grp = EmGroup('grp',None,None,'Test affichage du nom')
        a = grp.get_help_text()
        b = a
        b = 'Test de copie du nom'
        self.assertEqual(a,'Test affichage du nom')
        grp1 = EmGroup('grp')
        c = grp1.get_help_text()
        self.assertEqual(c, None)
        with self.assertRaises(ValueError): grp.get_help_text('ita')
            
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
        e_hash = 0x74657374677270333130363537393137343730343438343139303233393838303936373730323936353536393032313839313536333632313037343435323138313735343936303237373532343436303639363137
        self.assertEqual(grp.d_hash(), e_hash)

        
