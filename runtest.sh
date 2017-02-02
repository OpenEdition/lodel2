#!/bin/bash
#
# Usage : ./runtest [OPTIONS] [test_module[.test_class][ test_module2[.test_class2]...]
#########
#
# Running all discoverables tests :
# ./runtest
#
################
# -f, --failfast
#
#    Stop the test run on the first error or failure.
# -v --verbose
#
#   higher verbosity
#
# -d 0 : results are not displayed but stored in logfiles in /tmp/logXXXXXXX repository, with XXXXXXX a timestamp (default)
# -d 1 : results are displayed when tests finish and kept in logfiles in /tmp/logXXXXXXX repository, with XXXXXXX a timestamp
# -d 2 : results are displayed when tests finish, they are not stored
#
# Furthermore
################
# Most of the tests need an install of lodel for dependencies reasons
# For those which not need, prefix the python file by 'nc_' (example nc_test_query.py)
# they will be executed outside a lodel install
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

logdisplay=2;

while getopts ":d:" opt; do
    case $opt in
        d)
          logdisplay=$OPTARG
          ;;
        :)
          echo "Option -$OPTARG requires an argument, as it does not have we assume 0"
          ;;
    esac
done

if [[ $logdisplay -eq 2 ]]
then
    echo $logdisplay
    logdir=$(mktemp -td "lodel2_log_unittest_XXXXXXX")
else 
    if [ ! -d ./tmp ]
    then
        mkdir ./tmp
    fi
    timestamp=$(date +%s)
    logdir="$(dirname $(realpath $0))/tmp/log$timestamp"
    mkdir $logdir
fi

PYTHON='env python3'
ret_status=0

$PYTHON ./nocontext_tests.py $logdir $@ || ret_status=1
./runtest_context.sh $logdir $@ || ret_status=1

if [[ $logdisplay -eq 1 || $logdisplay -eq 2 ]]
then
    logfiles=$(ls $logdir)
    for logfile in $logfiles
    do
        cat $logdir/$logfile
    done
    if [[ $logdisplay -eq 2 ]]
    then 
        rm -rf $logdir
    fi
fi

exit $ret_status
