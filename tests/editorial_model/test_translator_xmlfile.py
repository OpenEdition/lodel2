#-*- coding: utf-8 -*-

import unittest
import tempfile
import os

import tests.loader_utils
from lodel.editorial_model.translator import picklefile
from lodel.editorial_model.translator import xmlfile
from lodel.editorial_model.model import EditorialModel
from lodel.editorial_model.components import *
from lodel.editorial_model.exceptions import *

class XmlFileTestCase(unittest.TestCase):
    
    def __init__(self, *args):
        super().__init__(*args)
        self.tmpfile = None

    def setUp(self):
        if self.tmpfile is not None:
            os.unlink(self.tmpfile)
        f_tmp, self.tmpfile = tempfile.mkstemp()
        os.close(f_tmp)

    def tearDown(self):
        if self.tmpfile is not None:
            os.unlink(self.tmpfile)

    def test_save(self):
        emmodel = EditorialModel("test model", description = "Test EM")
        cls1 = emmodel.new_class(   'testclass1',
                                    display_name = 'Classe de test 1',
                                    help_text = 'super aide')
        c1f1 = cls1.new_field('testfield1', data_handler = 'varchar')
        c1f2 = cls1.new_field('testfield2', data_handler = 'varchar')
        cls2 = emmodel.new_class('testclass2')
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
        
        self.assertEqual(new_model.d_hash(), emmodel.d_hash())

    def test_abstract_classes(self):
        """ Testing xmlfile abtract class handling """
        emmodel = EditorialModel("em_test", description = "Test model")
        cls1 = emmodel.new_class(   'testclass1',
                                    display_name = "test class 1",
                                    abstract = True)

        emmodel.save(xmlfile, filename=self.tmpfile)

        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())
    
    def test_groups(self):
        """ Testing xmlfile groups handling """
        emmodel = EditorialModel("em_test", description = "test model")
        emmodel.new_group(  'test_grp',
                            display_name = "Test group")

        emmodel.save(xmlfile, filename=self.tmpfile)
        
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())

    def test_groups_population(self):
        """ Testing xmlfile groups population handling """
        emmodel = EditorialModel("em_test", description = "test model")
        cls1 = emmodel.new_class(   'testclass1',
                                    display_name = "test class 1")
        cls2 = emmodel.new_class(   'testclass2',
                                    display_name = "test class 2")
        cls1f1 = cls1.new_field(    'testfield1',
                                    data_handler = 'varchar')
        cls2f1 = cls2.new_field(    'testfield2',
                                    data_handler = 'varchar')
        cls2f2 = cls2.new_field(    'testfield3',
                                    data_handler = 'varchar')
        grp1 = emmodel.new_group(  'test_grp',
                                    display_name = "Test group")
        grp2 = emmodel.new_group(  'test_grp2',
                                    display_name = "Test group2")
        grp1.add_components([cls1,cls2])
        grp2.add_components([cls1f1,cls2f1, cls2f2])
        emmodel.save(xmlfile, filename=self.tmpfile)
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())
    def test_groups_dependencies(self):
        """ Testing xmlfile groups population dependencies """
        emmodel = EditorialModel("em_test", description = "test model")
        grp1 = emmodel.new_group(  'test_grp',
                                    display_name = "Test group")
        grp2 = emmodel.new_group(  'test_grp2',
                                   display_name = "Test group2")
        grp3 = emmodel.new_group(  'test_grp3',
                                   display_name = "Test group3",
                                   depends = [grp1, grp2])
        
        emmodel.save(xmlfile, filename=self.tmpfile)
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())
    def test_emfield_with_prop_bool(self):
        """ Testing xmlfile with bool as property for datahandler """
        emmodel = EditorialModel("em_test", description = "test model")
        cls1 = emmodel.new_class(   'testclass1',
                                    display_name = "test class 1")
        cls1f1 = cls1.new_field(    'testfield1',
                                    data_handler = 'varchar',
                                    nullable = True)
        emmodel.save(xmlfile, filename=self.tmpfile)
        
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())

    def test_emfield_with_prop_tuple(self):
        """ Testing xmlfile with iterable as property for datahandler """
        emmodel = EditorialModel("em_test", description = "test model")
        cls1 = emmodel.new_class(   'testclass1',
                                    display_name = "test class 1")
        cls2 = emmodel.new_class(   'testclass2',
                                    display_name = "test class 2")
        cls1f1 = cls1.new_field(    'testfield1',
                                    data_handler = 'varchar')
        cls2f1 = cls2.new_field(    'testfield2',
                                    data_handler = 'list',
                                    allowed_classes = [cls1, cls2])
        cls2f1 = cls2.new_field(    'testfield3',
                                    data_handler = 'varchar',
                                    back_reference = (  'testclass2',
                                                        'testfield1'))
        emmodel.save(xmlfile, filename=self.tmpfile)
        
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())

    def test_emclass_with_ml_strings(self):
        """ Testing xmlfile mlstring handling in classes"""
        emmodel = EditorialModel("em_test", description = "test model")
        cls1 = emmodel.new_class(   'testclass1',
                                    display_name = {    'eng': "test class 1",
                                                        'fre': 'classe de test 1'})
        emmodel.save(xmlfile, filename=self.tmpfile)
        
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())

    def test_emfield_with_ml_strings(self):
        """ Testing xmlfile mlstring handling in data handlers """
        emmodel = EditorialModel("em_test", description = "test model")
        cls1 = emmodel.new_class(   'testclass1',
                                    display_name = "test class 1")
        cls1f1 = cls1.new_field(    'testfield1',
                                    display_name = {    'eng': 'test1',
                                                        'fre': 'test1'},
                                    data_handler = 'varchar')
        emmodel.save(xmlfile, filename=self.tmpfile)
        
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())

    def test_groups_with_ml_strings(self):
        """ Testing xmlfile groups handling """
        emmodel = EditorialModel("em_test", description = "test model")
        emmodel.new_group(  'test_grp',
                            display_name = {    'eng': "Test group",
                                                'fre': "Groupe de test"})

        emmodel.save(xmlfile, filename=self.tmpfile)
        
        emmodel_loaded = xmlfile.load(self.tmpfile)
        self.assertEqual(   emmodel.d_hash(),
                            emmodel_loaded.d_hash())

    def test_em_test(self):
        """ Testing xmlfile with the test editorial model """
        #emmodel = picklefile.load('tests/editorial_model.pickle')
        emmodel = picklefile.load('tests/em_test.pickle')

        emmodel.save(xmlfile, filename=self.tmpfile)
        emmodel.save(xmlfile, filename = 'empick.xml')
        emmodel_loaded = xmlfile.load(self.tmpfile)
        emmodel_loaded.save(xmlfile, filename = 'empick2.xml')
        #self.assertEqual(   emmodel.d_hash(),
                           # emmodel_loaded.d_hash())
