#!/bin/bash

usage() {
	echo -e "Usage : $0 instance_name (instance_dir|-u) [install_tpl] [em_file] [lidir]" >&2
	echo -e "\n\tIf -u given as first argument update instance's loader.py" >&2
	exit 1
}

cp_loader() {
	loader="${install_tpl}/loader.py"
	cp -Rv $loader $instdir/
	# Adding lib path to loader
	sed -i -E "s#^(LODEL2_LIB_ABS_PATH = )None#\1'$libdir'#" "$loader"
}


if [ $# -lt 2 ]
then
	echo "Not enough arguments" >&2
	usage
fi



name="$1"
instdir="$2"

libdir="$5"
libdir=${libdir:=[@]PKGPYTHONDIR[@]}
install_tpl="$3"

if [ $name == "monosite" ];then
    name=""
fi

if [ -z "$install_tpl" ]
then
	echo -e "Install template $install_tpl not found.\n" >&2
	usage
fi

em_file="$4"
if [ -z "$em_file" ]
then
	echo -e "Emfile $emfile not found.\n" >&2
	usage
fi


libdir=$(realpath $libdir)
install_tpl=$(realpath $install_tpl)
em_file=$(realpath $em_file)


if test ! -d $install_tpl
then
	echo "Install template directory '$install_tpl' not found"
	echo ""
	usage
fi

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
ln -sv $libdir/lodel/plugins $instdir/plugins
cp_loader

echo "BEGIN LS"
ls -la $instdir
echo "END LS"
# Adding instance name to conf
sed -i -E "s#^sitename = noname#sitename = $name#" "$conf"


echo -e "\nSite successfully created in $instdir"
echo -e "============================\n"
echo "Now you should edit files in '${instdir}/conf.d/' and then run : cd $instdir && make dyncode"
