#-*- coding: utf-8 -*-

import unittest

#import tests.loader_utils
from lodel.settings.settings_loader import SettingsLoader

#A dummy validator that only returns the value
def dummy_validator(value): return value
#A dummy validator that always fails
def dummy_validator_fails(value):  raise ValueError("Fake validaion error") 

class SettingsLoaderTestCase(unittest.TestCase):

    def test_merge_getsection(self):
        """Tests merge and getSection functions """
        settings = SettingsLoader('tests/settings/conf.d')
        a = settings.getsection('A')
        self.assertEqual(a,dict({"a":"a1","b":"b1,b2,b3","c":"toto","fhui":"njl"}))
        b = settings.getsection('B')
        self.assertEqual(b,dict({"ab":"art","bb":"bj,kl,mn","cb":"tatat"}))
        c = settings.getsection('C')
        self.assertEqual(c,dict({"ca":"a2","cb":"b4,b2,b3","cc":"titi"}))
        d = settings.getsection('D')
        
        for v in a:
            assert ('A','{"a":"a1","b":"b1,b2,b3","c":"toto","fhui":"njl"}')
        def maFonction(a):
            return a
        e=settings.getoption('A','a',maFonction)
        self.assertEqual(e,'a1')
        f=settings.getoption('B','bb',maFonction)
        self.assertEqual(f,"bj,kl,mn")
        g=settings.getremains()
        self.assertIsNotNone(g)
        e=settings.getoption('A','b',maFonction)
        e=settings.getoption('A','c',maFonction)
        e=settings.getoption('A','fhui',maFonction)
        f=settings.getoption('B','ab',maFonction)
        f=settings.getoption('B','cb',maFonction)
        f=settings.getoption('C','cb',maFonction)
        f=settings.getoption('C','ca',maFonction)
        f=settings.getoption('C','cc',maFonction)
       
        g=settings.getremains()
        self.assertEqual(g,[])
        
     
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
        self.assertEqual(set(sections), set(('lodel2.foobar',)))
        
    def test_variable_sections_fails(self):
        """ Testing behavior when no default section given for a non existing variable section """
        loader = SettingsLoader('tests/settings/settings_examples/var_sections.conf.d')
        with self.assertRaises(NameError):
            sections = loader.getsection('lodel2.notexisting')

