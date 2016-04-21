#!/bin/bash

usage() {
	echo "Usage : $0 instance_name instance_dir [lodel_libdir]" 1>&2
	exit 1
}

if [ $# -lt 2 ]
then
	echo "Not enough arguments" 1>&2
	usage
fi


name="$1"
instdir="$2"

libdir="$3"
libdir="${libdir:=$(realpath $(dirname $0)/..)}/"

loader="$instdir/loader.py"
conf="$instdir/conf.d/lodel2.ini"

if [ -e "$instdir" ]
then
	echo "Abording... "$instdir" exists" 1>&2
	exit 1
fi

echo "Creating lodel instance directory '$instdir'"
mkdir -pv "$instdir"

cp -Rv $libdir/install/* $instdir

# Adding lib path to loader
sed -i -E "s#^(LODEL2_LIB_ABS_PATH = )None#\1'$libdir'#" "$loader"
# Adding instance name to conf
sed -i -E "s#^sitename = noname#sitename = $name#" "$conf"

echo -e "\nInstance successfully created in $instdir"
echo -e "============================\n"
echo "Now you should edit '$settings' and then run : cd $instdir && make dbinit"
