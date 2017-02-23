#!/bin/bash

usage() {
	cat <<HELP_USAGE
Usage: $(basename $0) [options...] lodelsites_name [instance_dir] [install_path] [install_tpl]
	lodelsites_name: name of the lodelsites instance, only lower case alphas, numerics, -, _, are allowed
	instance_dir: path where the data and context folders will be set (defaults to /var/lodel2)
Options:
	-h, --help		give this help list
HELP_USAGE
	exit 1
}


[[ `grep -w "\-\-help\|\-.*h.*" <<< $@` ]] && usage


[[ -z $1 ]] && echo "Not enough arguments" && usage


name="$1"
install_dir=${2:=[@]LODEL2_VARDIR[@]}
install_tpl="$3"
context_dir_name="[@]LODELSITES_CTX_DIRNAME[@]"
datas_dir_name="[@]LODELSITES_DATA_DIRNAME[@]"


[[ -d "$install_dir/$name" ]] && echo "A multisite install $name already exists!" && usage 

echo "$MULTISITE_DATADIR"
lodelsites_ctx_dir="$install_dir/$name/$context_dir_name"
lodelsites_data_dir="$install_dir/$name/$datas_dir_name"


[[ ! "$name" =~ ^[abcdefghijklmnopqrstuvwxyz0-9_-]+$ ]] &&
	echo "Only lowercase alpha, numerics, '-', '_', are allowed in name" >&2 &&
	usage


echo "Creating directories"
mkdir -pv "$lodelsites_ctx_dir"
mkdir -pv "$lodelsites_data_dir"


echo "Modularization of the lodelsites context dir"
> "$lodelsites_ctx_dir/__init__.py"
echo "created '$lodelsites_ctx_dir/__init__.py' file"


#echo cp -R $install_tpl "${install_dir}/$name"
