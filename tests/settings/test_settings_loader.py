#-*- coding: utf-8 -*-

import unittest

from lodel.settings.utils import *
from lodel.settings.settings_loader import SettingsLoader

#A dummy validator that only returns the value
def dummy_validator(value): return value
#A dummy validator that always fails
def dummy_validator_fails(value):  raise ValueError("Fake validation error") 

class SettingsLoaderTestCase(unittest.TestCase):

    def test_merge_getsection(self):
        """Tests merge and getSection functions """
        settings = SettingsLoader('tests/settings/settings_examples/conf.d')
        def maFonction(a):
            return a
        e=settings.getoption('lodel2.A','a',maFonction)
        self.assertEqual(e,'a1')
        f=settings.getoption('lodel2.B','bb',maFonction)
        self.assertEqual(f,"bj,kl,mn")
        g=settings.getremains()
        self.assertIsNotNone(g)
        e=settings.getoption('lodel2.A','b',maFonction)
        e=settings.getoption('lodel2.A','c',maFonction)
        e=settings.getoption('lodel2.A','fhui',maFonction)
        f=settings.getoption('lodel2.B','ab',maFonction)
        f=settings.getoption('lodel2.B','cb',maFonction)
        f=settings.getoption('lodel2.C','cb',maFonction)
        f=settings.getoption('lodel2.C','ca',maFonction)
        f=settings.getoption('lodel2.C','cc',maFonction)
        f=settings.getoption('lodel2.C','a',maFonction)
        f=settings.getoption('lodel2.A.e','a',maFonction)
        f=settings.getoption('lodel2.A.e','titi',maFonction)
        g=settings.getremains()
        self.assertEqual(g,[])
        with self.assertRaises(SettingsError):
            loader = SettingsLoader('tests/settings/settings_examples/conf_raise.d')
    
    def test_merge(self):
        """ Test merge of multiple configuration files """
        loader = SettingsLoader('tests/settings/settings_examples/merge.conf.d')
        for value in ('a','b','c','d','e','f'):
            self.assertEqual(loader.getoption('lodel2', value, dummy_validator), value)
            self.assertEqual(loader.getoption('lodel2.othersection', value, dummy_validator), value)

    def test_merge_conflict(self):
        """ Test merge fails because of duplicated keys """
        with self.assertRaises(SettingsError):
            loader = SettingsLoader('tests/settings/settings_examples/bad_merge.conf.d')
     
    def test_getoption_simple(self):
        """ Testing behavior of getoption """
        loader = SettingsLoader('tests/settings/settings_examples/simple.conf.d')
        value = loader.getoption('lodel2.foo.bar', 'foo', dummy_validator)
        self.assertEqual(value, "42")
        value = loader.getoption('lodel2.foo.bar', 'foobar', dummy_validator)
        self.assertEqual(value, "hello world")

    def test_variable_sections(self):
        """ Testing variable section recognition """
        loader = SettingsLoader('tests/settings/settings_examples/var_sections.conf.d')
        sections = loader.getsection('lodel2.tests')
        self.assertEqual(   set(sections),
                            set((   'lodel2.tests.section1', 
                                    'lodel2.tests.section2')))
    
    def test_variable_sections_default(self):
        """ Testing variable section default value handling """
        loader = SettingsLoader('tests/settings/settings_examples/var_sections.conf.d')
        sections = loader.getsection('lodel2.notexisting', 'foobar')
        self.assertEqual(set(sections), set(('lodel2.notexisting.foobar',)))
        
    def test_variable_sections_fails(self):
        """ Testing behavior when no default section given for a non existing variable section """
        loader = SettingsLoader('tests/settings/settings_examples/var_sections.conf.d')
        with self.assertRaises(NameError):
            sections = loader.getsection('lodel2.notexisting')
    
    @unittest.skip("Waiting implementation")
    def test_remains(self):
        """ Testing the remains method of SettingsLoader """
        loader = SettingsLoader('tests/settings/settings_examples/remains.conf.d')
        pass #TO BE DONE LATER
