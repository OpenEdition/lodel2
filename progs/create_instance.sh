#!/bin/bash
# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


usage() {
	echo -e "Usage : $0 instance_name (instance_dir|-u) [install_tpl] [em_file] [lidir]" >&2
	echo -e "\n\tIf -u given as first argument update instance's loader.py" >&2
	exit 1
}

loader_update() {
	libdir=$1
	install_tpl=$2
	instdir=$3
	lib_abs_path=$(dirname $libdir)
	cp -Rv $install_tpl/loader.py $instdir/loader.py
	# Adding lib path to loader
	sed -i -E "s#^(LODEL2_LIB_ABS_PATH = )None#\1'$lib_abs_path'#" "$instdir/loader.py"
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

echo "LIBDIR : $libdir"

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
      loader_update "$libdir" "$install_tpl" "$instdir"
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
loader_update "$libdir" "$install_tpl" "$instdir"

# Adding instance name to conf
sed -i -E "s#^sitename = noname#sitename = $name#" "$conf"


echo -e "\nSite successfully created in $instdir"
echo -e "============================\n"
echo "Now you should edit files in '${instdir}/conf.d/' and then run : cd $instdir && make dyncode"
