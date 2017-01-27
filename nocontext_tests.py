#-*- coding: utf-8 -*-

##@brief Loader for tests which do not need an lodel installation
#
# Options
################
# 
# @note We can pass the path to a directory to write results file, nocontext_tests.log
# It has to be at first, otherwise it will not be taken 
# and the default one, current directory, will be used.
# The results are not displayed, only stored in nocontext_tests.log
#
# -f, --failfast
#
#    Stop the test run on the first error or failure.
# -v --verbose
#
#   higher verbosity
#
#

import sys, os, os.path
import unittest


loader = unittest.TestLoader()

if ((len(sys.argv) > 1) and (sys.argv[1].startswith('-')) is False):
	dpath = sys.argv[1]
else:
	dpath = '.'

suite = loader.discover('tests', pattern='nc_test*.py')
with open(dpath+'/nocontext_tests.log', 'w') as logfile:
    unittest.TextTestRunner(
    	logfile,
        failfast = '-f' in sys.argv,
        verbosity = 2 if '-v' in sys.argv else 1).run(suite)
