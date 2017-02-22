#-*- coding: utf-8 -*-

import unittest
import os.path

from lodel.settings.utils import *
from lodel.plugin.exceptions import *
from lodel.settings.settings_loader import SettingsLoader
from lodel.validator.validator import *



#A dummy validator that only returns the value
def dummy_validator(value): return value
#A dummy validator that always fails
def dummy_validator_fails(value):  raise ValueError("Fake validation error") 

def write_list_validator(value):
    res = ''
    errors = list()
    for elt in value:
        res += dummy_validator(elt) + ','
    return res[:len(res)-1]
        
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
        self.assertEqual(len(g),0)
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
        value = loader.getoption('lodel2.foo.bar', 'foo_bar', dummy_validator)
        self.assertEqual(value, "foobar")
        value = loader.getoption('lodel2.foo.bar', 'foo.bar', dummy_validator)
        self.assertEqual(value, "barfoo")

    def test_getoption_multiple_time(self):
        """ Testing the behavior when doing 2 time the same call to getoption """
        loader = SettingsLoader('tests/settings/settings_examples/simple.conf.d')
        value = loader.getoption('lodel2.foo.bar', 'foo', dummy_validator)
        value = loader.getoption('lodel2.foo.bar', 'foo', dummy_validator)
        value = loader.getoption('lodel2.foo.bar', 'foo', dummy_validator)
        value = loader.getoption('lodel2.foo.bar', 'foo', dummy_validator)


    def test_geoption_default_value(self):
        """ Testing behavior of default value in getoption """
        loader = SettingsLoader('tests/settings/settings_examples/simple.conf.d')
        # for non existing keys in file
        value = loader.getoption('lodel2.foo.bar', 'foofoofoo', dummy_validator, 'hello 42')
        self.assertEqual(value, 'hello 42')
        # for non existing section in file
        value = loader.getoption('lodel2.foofoo', 'foofoofoo', dummy_validator, 'hello 42')
        self.assertEqual(value, 'hello 42')

    def test_geoption_invalid_default_value(self):
        """ Testing the behavior when the default value is invalid """
        loader = SettingsLoader('tests/settings/settings_examples/simple.conf.d')
        mandatory_validator = Validator('string', none_is_valid=False)
        with self.assertRaises(SettingsErrors):
            value = loader.getoption(
                'lodel2.foo.bar', 'foofoofooDEFAULT', mandatory_validator)
            loader.raise_errors()

    def test_getoption_complex(self):
        """ Testing behavior of getoption with less simple files & confs """

        expected = {
            'lodel2.editorialmodel': {
                'lib_path': '/tmp',
                'foo_bar': '42',
                'foo.bar': '1337',
                'example': 'foobar',
            },
            'lodel2.conf1': {
                'conf_key': 'woot',
                'conf_value': '42',
            },
            'lodel2.conf2': {
                'conf_foo': 'bar',
            },
            'lodel2.foo.foo': {
                'foobar': 'barfoo',
            },
            'lodel2.bar.foo': {
                'foobar': 'barfoo',
                'barfoo': '42',
            },
            'lodel2.bar.bar': {
                'toto': 'tata',
            }
        }

        loader = SettingsLoader('tests/settings/settings_examples/complex.conf.d')
        for section in expected:
            for key, expected_value in expected[section].items():
                value = loader.getoption(   section,
                                            key,
                                            dummy_validator)
                self.assertEqual(value, expected_value)

                

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
    
    def test_remains(self):
        """ Testing the remains method of SettingsLoader """
        loader = SettingsLoader('tests/settings/settings_examples/remains.conf.d')
        values = {
            'lodel2.section': [ chr(i) for i in range(ord('a'), ord('f')) ],
            'lodel2.othersection': [ chr(i) for i in range(ord('a'), ord('f')) ],
        }
        
        expt_rem = []
        for section in values:
            for val in values[section]:
                expt_rem.append('%s:%s' % (section, val))

        self.assertEqual(sorted(expt_rem), sorted(loader.getremains().keys()))

        for section in values:
            for val in values[section]:
                loader.getoption(section, val, dummy_validator)
                expt_rem.remove('%s:%s' % (section, val))
                self.assertEqual(   sorted(expt_rem),
                                    sorted(loader.getremains().keys()))
    def test_setoption(self):
        loader=SettingsLoader('tests/settings/settings_examples/conf_set.d')
        loader.setoption('lodel2.A','fhui','test ok',dummy_validator)
        loader=SettingsLoader('tests/settings/settings_examples/conf_set.d')
        option=loader.getoption('lodel2.A','fhui',dummy_validator)
        self.assertEqual(option,'test ok')
        loader.setoption('lodel2.A','fhui','retour',dummy_validator)
        loader=SettingsLoader('tests/settings/settings_examples/conf_set.d')
        option=loader.getoption('lodel2.A','fhui',dummy_validator)
        self.assertEqual(option,'retour')
        cblist=('test ok1','test ok2','test ok3')
        loader.setoption('lodel2.C','cb',cblist,write_list_validator)
        loader=SettingsLoader('tests/settings/settings_examples/conf_set.d')
        option=loader.getoption('lodel2.C','cb',dummy_validator)
        self.assertEqual(option,'test ok1,test ok2,test ok3')
        cblist=('b4','b2','b3')
        loader.setoption('lodel2.C','cb',cblist,write_list_validator)
        loader=SettingsLoader('tests/settings/settings_examples/conf_set.d')
        option=loader.getoption('lodel2.C','cb',dummy_validator)
        self.assertEqual(option,'b4,b2,b3')
        
    def test_saveconf(self):
        loader=SettingsLoader('tests/settings/settings_examples/conf_save.d')
        newsec=dict()
        newsec['lodel2.A'] = dict()
        newsec['lodel2.A']['fhui'] = 'test ok'
        newsec['lodel2.A']['c'] = 'test ok'
        newsec['lodel2.A.e'] = dict()
        newsec['lodel2.A.e']['a'] = 'test ok'
        validators = dict()
        validators['lodel2.A'] = dict()
        validators['lodel2.A']['fhui'] = dummy_validator
        validators['lodel2.A']['c'] = dummy_validator
        validators['lodel2.A.e'] = dict()
        validators['lodel2.A.e']['a'] = dummy_validator
        
        loader.saveconf(newsec,validators)
        loader=SettingsLoader('tests/settings/settings_examples/conf_save.d')
        option=loader.getoption('lodel2.A','fhui',dummy_validator)
        self.assertEqual(option,'test ok')
        option=loader.getoption('lodel2.A','c',dummy_validator)
        self.assertEqual(option,'test ok')
        option=loader.getoption('lodel2.A.e','a',dummy_validator)
        self.assertEqual(option,'test ok')
        
        newsec['lodel2.A']['fhui']='retour'
        newsec['lodel2.A']['c']='toto'
        newsec['lodel2.A.e']['a']='ft'
        
        loader.saveconf(newsec,validators)
        loader=SettingsLoader('tests/settings/settings_examples/conf_save.d')
        option=loader.getoption('lodel2.A','fhui',dummy_validator)
        self.assertEqual(option,'retour')
        option=loader.getoption('lodel2.A','c',dummy_validator)
        self.assertEqual(option,'toto')
        option=loader.getoption('lodel2.A.e','a',dummy_validator)
        self.assertEqual(option,'ft')

    def test_setoption_default_value(self):
        loader = SettingsLoader('tests/settings/settings_examples/conf_setdef.d')
            
        # for non existing keys in file
        value = loader.getoption('lodel2.foo.bar', 'foofoofoo', dummy_validator, 'hello 42')
        self.assertEqual(value, 'hello 42')
        # for non existing section in file
        value = loader.getoption('lodel2.foofoo', 'foofoofoo', dummy_validator, 'hello 42')
        self.assertEqual(value, 'hello 42')
        
        loader.setoption('lodel2.foo.bar', 'foofoofoo', 'test ok', dummy_validator)
        loader.setoption('lodel2.foofoo', 'foofoofoo', 'test ok', dummy_validator)
        self.assertTrue(os.path.isfile('tests/settings/settings_examples/conf_setdef.d/generated.ini'))
        
        loader = SettingsLoader('tests/settings/settings_examples/conf_setdef.d')
        value = loader.getoption('lodel2.foofoo', 'foofoofoo', dummy_validator)
        self.assertEqual(value, 'test ok')
        value = loader.getoption('lodel2.foo.bar', 'foofoofoo', dummy_validator)
        self.assertEqual(value, 'test ok')
        
        os.remove('tests/settings/settings_examples/conf_setdef.d/generated.ini')
        
