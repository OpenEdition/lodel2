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
        cls2 = emmodel.new_class('testclass2') #, display_name = 'Classe de test 2', help_text = 'super aide')
        c2f1 = cls2.new_field('testfield1', data_handler = 'varchar')
        c2f2 = cls2.new_field('testfield2', data_handler = 'varchar')

        grp1 = emmodel.new_group('testgroup1')
        grp1.add_components((cls1, c1f1))
        grp2 = emmodel.new_group('testgroup2')
        grp2.add_components((cls2, c1f2, c2f1, c2f2))

        grp2.add_dependencie(grp1)
        
        f_tmp, file_name = tempfile.mkstemp()
        os.close(f_tmp)
        
        emmodel.save(xmlfile, filename=file_name)
        new_model = EditorialModel.load(xmlfile, filename=file_name)
        
        f_tmp, fname = tempfile.mkstemp()
        os.close(f_tmp)
        
        new_model.save(xmlfile, filename=fname)

        os.unlink(file_name)
        os.unlink(fname)           

        self.assertNotEqual(id(new_model), id(emmodel))

        new_cls2 = new_model.all_classes('testclass2')
        em_cls2 = emmodel.all_classes('testclass2')
        
        new_cls1 = new_model.all_classes('testclass1')
        em_cls1 = emmodel.all_classes('testclass1')

        self.assertEqual(new_cls2.d_hash(),em_cls2.d_hash())
        self.assertEqual(new_model.all_classes('testclass1').d_hash(), cls1.d_hash())
        self.assertEqual(new_model.all_groups('testgroup2').d_hash(), grp2.d_hash())
        
        # Pb de d_hash required
        emmgrp1 = new_model.all_groups('testgroup1')
        self.assertEqual(emmgrp1.d_hash(), grp1.d_hash())
        
        #self.assertEqual(new_model.all_groups('testgroup1').d_hash(), emmodel.all_groups('testgroup1').d_hash())
        #self.assertEqual(new_model.d_hash(), emmodel.d_hash())



