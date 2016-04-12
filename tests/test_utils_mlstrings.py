#-*- coding: utf-8 -*-

import unittest
import copy


import tests.loader_utils
from lodel.utils.mlstring import MlString

class MlStringTestCase(unittest.TestCase):
    
    examples = {
            'eng': 'Hello world !',
            'fre': 'Bonjour monde !',
            'ger': 'Hallo welt !',
        }

    def test_init_str(self):
        """ Test MlString instanciation with string as argument """
        testlangs = ['eng', 'fre']
        teststrs = ['hello', 'Hello world !', '{helloworld !!!]}']
        for lang in testlangs:
            for teststr in teststrs:
                MlString.default_lang(lang)
                mls_test = MlString(teststr)
                self.assertEqual(teststr, str(mls_test))
                self.assertEqual(teststr, mls_test.get(lang))

    def test_init_dict(self):
        """ Test MlString instanciation with dict as argument """
        mls = MlString(self.examples)
        for lang, val in self.examples.items():
            self.assertEqual(mls.get(lang), val)

    def test_init_json(self):
        """ Test MlString instanciation using a json string """
        testval = '{"eng":"Hello world !", "fre":"Bonjour monde !", "ger":"Hallo welt !"}'
        mls = MlString.from_json(testval)
        for lang in self.examples:
            self.assertEqual(mls.get(lang), self.examples[lang])

    def test_get(self):
        """ Test MlString get method """
        mls = MlString(self.examples)
        for lang, val in self.examples.items():
            self.assertEqual(mls.get(lang), val)
        # A lang that is not set
        self.assertEqual(mls.get('esp'), str(mls))
        # A deleted lang
        mls.set('fre', None)
        self.assertEqual(mls.get('fre'), str(mls))

    def test_eq(self):
        """ Test MlString comparison functions """
        for val in ['hello world', self.examples]:
            mls1 = MlString(val)
            mls2 = MlString(val)
            self.assertTrue(mls1 == mls2)
            self.assertEqual(hash(mls1), hash(mls2))

        mls1 = MlString('Hello world !')
        mls2 = MlString('hello world !')
        self.assertTrue(mls1 != mls2)
        self.assertNotEqual(hash(mls1), hash(mls2))

        modexamples = copy.copy(self.examples)
        modexamples['eng'] = 'hello world !'
        mls1 = MlString(modexamples)
        mls2 = MlString(self.examples)
        self.assertTrue(mls1 != mls2)
        self.assertNotEqual(hash(mls1), hash(mls2))

        mls1 = MlString(self.examples)
        mls2 = MlString(self.examples)
        mls1.set('eng', None)
        self.assertTrue(mls1 != mls2)
        self.assertNotEqual(hash(mls1), hash(mls2))
        
        mls1 = MlString(self.examples)
        mls2 = MlString(self.examples)
        mls1.set('eng', 'hello world !')
        self.assertTrue(mls1 != mls2)
        self.assertNotEqual(hash(mls1), hash(mls2))


    def test_d_hash(self):
        """ Test if the hash method is deterministic """
        mls1 = MlString('Hello world !')
        self.assertEqual(mls1.d_hash(),305033383450738439650269714534939972534)
