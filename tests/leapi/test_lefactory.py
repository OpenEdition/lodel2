#-*- coding: utf-8 -*-

import unittest
import random

import tests.loader_utils
from lodel.editorial_model.model import EditorialModel
from lodel.leapi import lefactory

class LeFactoryTestCase(unittest.TestCase):
    
    model = None

    @classmethod
    def setUpClass(cls):
        """ Generate an example model for this TestCase """
        model = EditorialModel(
                                    "test_model",
                                    description = "Model for LeFactoryTestCase"
        )
        cls1 = model.new_class('testclass1')
        cls2 = model.new_class('testclass2')
        cls3 = model.new_class('testclass3', parents = [cls2])
        cls4 = model.new_class('testclass4', parents = [cls1, cls3])
        cls5 = model.new_class('testclass5', parents = [cls4])
        cls6 = model.new_class('testclass6', parents = [cls5])

        cls1.new_field('testfield1', data_handler='varchar')
        cls1.new_field('testfield2', data_handler='varchar', nullable = True)
        cls1.new_field('testfield3', data_handler='varchar', max_length=64)
        cls1.new_field('testfield4', data_handler='varchar', max_length=64, nullable=False, uniq=True)
        cls1.new_field('id', data_handler='integer', primary_key = True)

        cls5.new_field('id2', data_handler='varchar', primary_key = True)

        cls.model = model
    
    def test_emclass_sorted_by_deps(self):
        """ Test the function that sort EmClass by dependencies """
        cls_list = self.model.classes()
        
        for _ in range(100): #Bad sorts algorithm can have random behavior
            random.shuffle(cls_list)
            sorted_cls = lefactory.emclass_sorted_by_deps(cls_list)
            seen = set() # Stores the EmClass allready seen will walking through array
            for emclass in sorted_cls:
                for parent in emclass.parents_recc:
                    self.assertIn(parent, seen)
                seen |= set((emclass,))

    def test_generated_code_syntax(self):
        """ Test the function that generate LeObject childs classes code"""
        pycode = lefactory.dyncode_from_em(self.model)
        pycomp_code = compile(pycode, "dyn.py", 'exec')
        exec(pycomp_code, globals())
        
