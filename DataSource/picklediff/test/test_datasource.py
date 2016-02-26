#-*- coding:utf-8 -*-

import unittest
import tempfile
import os, os.path

import leapi.test.utils
from Lodel.settings import Settings
from DataSource.picklediff.leapidatasource import LeapiDataSource
from leapi.lecrud import _LeCrud
from Lodel import logger
from Lodel.utils.mlstring import MlString

class PickleDiffDataSourceTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ Set settings for pickle datasource """
        logger.remove_console_handlers()

        _, filename = tempfile.mkstemp(prefix="picklediff_test_")
        cls.filename = filename
        if os.path.isfile(filename):
            os.unlink(filename)
        cls.ds_package_bck = Settings.ds_package
        cls.ds_opt_bck = Settings.datasource_options
        Settings.ds_package = 'picklediff'
        Settings.datasource_options = { 'filename': filename }
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    
    @classmethod
    def tearDownClass(cls):
        """ Delete temporary file """
        if os.path.isfile(cls.filename):
            os.unlink(cls.filename)
        leapi.test.utils.cleanup(cls.tmpdir)
        Settings.ds_package = cls.ds_package_bck
        Settings.datasource_options = cls.ds_opt_bck
        _LeCrud._datasource = None

    def test_insert(self):
        from dyncode import Article
        uid = Article.insert({'titre': 'fooBar', 'soustitre': 'Barfoo'})
        res = Article.get([])

        e_titre = MlString(default_value = 'fooBar')
        e_stitre = MlString(default_value = 'Barfoo')

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].uidget(), uid)
        self.assertEqual(res[0].titre, e_titre)
        self.assertEqual(res[0].soustitre, e_stitre)
    

    def test_load(self):
        from dyncode import Article, LeCrud
        
        uid = Article.insert({'titre': 'wowwo', 'soustitre': 'randomdsfsdfqsofjze'})
        orig = Article.get([('lodel_id','=', uid)])

        new_ds = LeapiDataSource(self.filename)
        Article._datasource = new_ds
        # Article._datasource = 42 #uncomment this line to verify that this hack works
        new = Article.get([('lodel_id','=', uid)])
        self.assertEqual(orig, new)
