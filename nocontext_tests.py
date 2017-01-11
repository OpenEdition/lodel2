#-*- coding: utf-8 -*-

import sys, os, os.path
import unittest
import nocontext_tests

loader = unittest.TestLoader()

suite = loader.discover('tests', pattern='nc_test*.py')
with open(sys.argv[1]+'/nocontext_tests.log', 'w') as logfile:
    unittest.TextTestRunner(
    	logfile,
        failfast = '-f' in sys.argv,
        verbosity = 2 if '-v' in sys.argv else 1).run(suite)
