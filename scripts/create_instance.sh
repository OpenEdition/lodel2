#!/bin/bash

usage() {
	echo -e "Usage : $0 instance_name (instance_dir|-u) [lodel_libdir]" 1>&2
	echo -e "\n\tIf -u given as first argument update instance's loader.py" 1>&2
	exit 1
}

cp_loader() {
	cp -Rv $libdir/install/loader.py $instdir/
	# Adding lib path to loader
	sed -i -E "s#^(LODEL2_LIB_ABS_PATH = )None#\1'$libdir'#" "$loader"
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

if [ $1 = '-u' ]
then
	#Update instance
	cp_loader
	exit 0
fi

if [ -e "$instdir" ]
then
	echo "Abording... "$instdir" exists" 1>&2
	exit 1
fi

echo "Creating lodel instance directory '$instdir'"
mkdir -pv "$instdir"
mkdir -pv "$instdir/sessions"
chmod 700 "$instdir/sessions"

#cp -Rv $libdir/install/* $instdir
cp -Rv $libdir/install/conf.d $instdir/
cp -Rv $libdir/examples/em_test.pickle $instdir/editorial_model.pickle
ln -sv $libdir/install/Makefile $instdir/Makefile
ln -sv $libdir/install/lodel_admin.py $instdir/lodel_admin.py
ln -sv $libdir/plugins $instdir/plugins
cp_loader
# Adding instance name to conf
sed -i -E "s#^sitename = noname#sitename = $name#" "$conf"


echo -e "\nInstance successfully created in $instdir"
echo -e "============================\n"
echo "Now you should edit files in '${instdir}/conf.d/' and then run : cd $instdir && make dyncode"
