#!/bin/bash

usage() {
	echo -e "Usage : $0 instance_name (instance_dir|-u) [install_tpl] [em_file]" 1>&2
	echo -e "\n\tIf -u given as first argument update instance's loader.py" 1>&2
	exit 1
}

cp_loader() {
	cp -Rv $install_tpl/loader.py $instdir/
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


libdir=[@]PKGPYTHONDIR[@]
install_tpl="$3"
[ -z "$install_tpl" ] && usage
em_file="$4"
[ -z "$em_file" ] && usage


libdir=$(realpath $libdir)
install_tpl=$(realpath $install_tpl)
em_file=$(realpath $em_file)


if test ! -d $install_tpl
then
	echo "Install template directory '$install_tpl' not found"
	echo ""
	usage
fi

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

#cp -Rv $install_tpl/* $instdir
cp -Rv $install_tpl/conf.d $instdir/
cp -Rv $em_file $instdir/editorial_model.pickle
ln -sv $install_tpl/Makefile $instdir/Makefile
ln -sv $install_tpl/lodel_admin.py $instdir/lodel_admin.py
ln -sv $libdir/plugins $instdir/plugins
cp_loader
# Adding instance name to conf
sed -i -E "s#^sitename = noname#sitename = $name#" "$conf"


echo -e "\nInstance successfully created in $instdir"
echo -e "============================\n"
echo "Now you should edit files in '${instdir}/conf.d/' and then run : cd $instdir && make dyncode"