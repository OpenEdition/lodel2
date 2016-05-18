#-*- coding: utf-8 -*-

import unittest
import tempfile
import os

import tests.loader_utils
from lodel.editorial_model.translator import xmlfile
from lodel.editorial_model.model import EditorialModel
from lodel.editorial_model.components import *
from lodel.editorial_model.exceptions import *

class XmlFileTestCase(unittest.TestCase):
    
    def test_save(self):
        emmodel = EditorialModel("test model", description = "Test EM")
        cls1 = emmodel.new_class('testclass1', display_name = 'Classe de test 1', help_text = 'super aide')
        c1f1 = cls1.new_field('testfield1', data_handler = 'varchar')
        c1f2 = cls1.new_field('testfield2', data_handler = 'varchar')
        cls2 = emmodel.new_class('testclass2', display_name = 'Classe de test 2', help_text = 'super aide')
        c2f1 = cls2.new_field('testfield1', data_handler = 'varchar')
        c2f2 = cls2.new_field('testfield2', data_handler = 'varchar')

        grp1 = emmodel.new_group('testgroup1')
        grp1.add_components((cls1, c1f1))
        grp2 = emmodel.new_group('testgroup2')
        grp2.add_components((cls2, c1f2, c2f1, c2f2))

        grp2.add_dependencie(grp1)
        
        filename = {'filename' : 'savemodel.xml'}
        emmodel.save(xmlfile, **filename)
        new_model = EditorialModel.load(xmlfile, **filename)
        
        fname = {'filename' : 'savemodel_bis.xml'}
        new_model.save(xmlfile, **fname)
        #new_model2 = EditorialModel.load(xmlfile, **fname)
    
        self.assertNotEqual(id(new_model), id(emmodel))

        #self.assertEqual(new_model.d_hash(), new_model2.d_hash())
        new_cls2 = new_model.all_classes('testclass2')
        em_cls2 = emmodel.all_classes('testclass2')
        new_fields = new_cls2.fields()
        em_fields = em_cls2.fields()
        #for fld in new_fields:
        #    print(fld.d_hash())
        #for fld in em_fields:
        #    print(fld.d_hash())
        # fields OK
        
        new_cls1 = new_model.all_classes('testclass1')
        em_cls1 = emmodel.all_classes('testclass1')
        new_fields = new_cls1.fields()
        em_fields = em_cls1.fields()
        #for fld in new_fields:
        #    print(fld.d_hash())
        #for fld in em_fields:
        #    print(fld.d_hash())
        # fields OK
        
        # super().d_hash() OK si display_name et help_text dans cls2
        self.assertEqual(new_cls2.d_hash(),em_cls2.d_hash())
        self.assertEqual(new_model.all_classes('testclass1').d_hash(), cls1.d_hash())
        self.assertEqual(new_model.all_groups('testgroup2').d_hash(), grp2.d_hash())
        # Pb de d_hash required
        emmgrp1 = new_model.all_groups('testgroup1')
        for rep in emmgrp1.required_by:
            print(emmgrp1.required_by[rep])
        self.assertEqual(emmgrp1.d_hash(), grp1.d_hash())
        
        self.assertEqual(new_model.all_groups('testgroup1').d_hash(), emmodel.all_groups('testgroup1').d_hash())



        self.assertEqual(new_model.d_hash(), emmodel.d_hash())




