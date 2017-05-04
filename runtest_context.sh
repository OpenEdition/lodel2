#!/bin/bash
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


# Usage : ./runtest [OPTIONS] [test_module[.test_class][ test_module2[.test_class2]...]
#########
#
# Options list :
################
#
# -b, --buffer
#
#    The standard output and standard error streams are buffered during the test run. Output during a passing test is discarded. Output is echoed normally on test fail or error and is added to the failure messages.
#
# -c, --catch
#
#    Control-C during the test run waits for the current test to end and then reports all the results so far. A second control-C raises the normal KeyboardInterrupt exception.
#
#
# -f, --failfast
#
#    Stop the test run on the first error or failure.
#
# -h, --help
#
#    Get some help
#
# -v, --verbose
#
#   higher verbosity
#
# Examples :
############
#
# Running all discoverables tests :
# ./runtest
#
# Running only Em test about component object (only tests about the __init__ and modify_rank methods) with higher verbosity and failfast :
# ./runtest -fv EditorialModel.test.test_component.TestInit EditorialModel.test.test_component.TestModifyRank
#
#
# Running only Em tests
# ./runtest discover EditorialModel
#
# More details :
################
#
# https://docs.python.org/3.4/library/unittest.html
#
if test ! -f lodel/buildconf.py
then
	echo "You have to build the project before running the tests"
	echo "See README"
	exit 1
fi

PYTHON='env python3'
testdir=$(mktemp -td "lodel2_unittest_instance_XXXXXXXX")
install_model_dir="[@]INSTALLMODEL_DIR[@]"
if [ ! -d "$install_model_dir" ]
then
	install_model_dir="$(dirname $0)/progs/slim/install_model/"
fi
libdir="$(dirname $(realpath $0))/lodel"
rmdir $testdir
progs/create_instance test_instance $testdir "$install_model_dir" examples/em_test.pickle "$libdir"
echo progs/create_instance test_instance $testdir "$install_model_dir" examples/em_test.pickle "$libdir"
cp -R examples $testdir
cp -R tests $testdir
cd $testdir
chmod +x lodel_admin.py
rm -R conf.d && mv tests/tests_conf.d conf.d
make
make refresh_plugins
$PYTHON loader.py $@ && ret_status=0 || ret_status=1

rm -Rf $testdir

exit $ret_status
