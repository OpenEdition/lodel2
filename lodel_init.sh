#!/bin/bash

#
# Create a Lodel2 instance
#-------------------------
#
# Usage : ./lodel_init.sh instance_name instance_path [lodel2_lib_path]
#
# This script creates a new Lodel2 instance.
#
# It make a copy of install/ directory + some substitution in the instance_settings.py file
# and then it generates dynamic code
#


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
libdir="${libdir:=$(realpath $(dirname $0))}"

emfilename="em.json"
settings="$instdir/instance_settings.py"
em="$instdir/em.json"
dyncode="$instdir/${name}.py"

if [ -e "$instdir" ]
then
	echo "Abording... "$instdir" exists" 1>&2
	exit 1
fi

echo "Creating lodel instance directory '$instdir'"
mkdir -pv "$instdir"

cp -v $libdir/install/* $instdir
rm -fv $instdir/__init__.py

sed -i -e "s#LODEL2_LIB_ABS_PATH#$libdir#" "$settings"
sed -i -e "s#LODEL2_INSTANCE_NAME#$name#" "$settings"

echo "Generating dynamic code"
cd "$instdir"
make refreshdyn
echo "Cleaning instance directory"
make clean

echo -e "\nInstance successfully created in $instdir"
echo -e "============================\n"
echo "Now you should edit '$settings' and then run : cd $instdir && make dbinit"
