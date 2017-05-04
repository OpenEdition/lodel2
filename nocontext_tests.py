#
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


# @brief Loader for tests which do not need an lodel installation
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

import sys
import os
import os.path
import unittest


loader = unittest.TestLoader()

if ((len(sys.argv) > 1) and (sys.argv[1].startswith('-')) is False):
    dpath = sys.argv[1]
else:
    dpath = '.'

suite = loader.discover('tests', pattern='nc_test*.py')
with open(dpath + '/nocontext_tests.log', 'w') as logfile:
    unittest.TextTestRunner(
        logfile,
        failfast='-f' in sys.argv,
        verbosity=2 if '-v' in sys.argv else 1).run(suite)
