#!/bin/bash

usage() {
	echo -e "Usage : $0 LODELSITES_NAME [install_path] [install_tpl]"
	exit 1
}

if [ $# -lt 1 ]
then
    usage
fi

name="$1"
install_dir="$2"
install_dir=${vardir:=[@]LODEL2_VARDIR[@]}
install_tpl="$3"

if echo $name | grep -Ev '^[a-z0-9_-]+$' &>/dev/null
then
	echo "Only alnum lowercase '-', '_' allowed in name"
	usage
fi

echo cp -R $install_tpl "${install_dir}/$name"
