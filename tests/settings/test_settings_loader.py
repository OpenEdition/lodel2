#-*- coding: utf-8 -*-

import unittest

import tests.loader_utils
from lodel.settings.settings_loader import SettingsLoader

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
        
        
        
