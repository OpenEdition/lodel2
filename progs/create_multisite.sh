#!/bin/bash

usage() {
	cat <<HELP_USAGE
Usage: $(basename $0) lodelsites_name [instance_dir] [install_path] [install_tpl]
	lodelsites_name: name of the lodelsites instance, only lower case alphas, numerics, -, _, are allowed
	instance_dir: path where the data and context folders will be set (defaults to /var/lodel2)
Options:
	-h, --help		give this help list
HELP_USAGE
	exit 1
}

conf_file_subst() {
	#Make substitution in file given as argument
	#$1 filename
	#$2 instance_name
	sed -i "s/@@@INSTANCE_NAME@@@/$2/g" $1
}

[ $# -lt 1 -o $# -gt 4 ] && usage

name="$1"
install_dir=$2
install_dir=${install_dir:=[@]LODEL2_VARDIR[@]}
install_tpl="$3"
install_tpl=${install_tpl:=[@]MULTISITE_INSTALLMODEL_DIR[@]}
context_dir_name="[@]LODELSITES_CTX_DIRNAME[@]"
datas_dir_name="[@]LODELSITES_DATA_DIRNAME[@]"
libdir="[@]LODEL2_LIBDIR[@]"
#Inconsistency with the fact that we can give the install template in argument
mono_model=[@]INSTALLMODEL_DIR[@]

if [[ ! "$name" =~ ^[abcdefghijklmnopqrstuvwxyz0-9_-]+$ ]]
then
	echo -e "Only lowercase alpha, numerics, '-', '_', are allowed in name\n" >&2
	usage
fi
if [ -d "$install_dir/$name" ]
then
	echo "A multisite install $name already exists\n" >&2
	usage 
fi


instance_dir="$install_dir/$name"
lodelsites_ctx_dir="$instance_dir/$context_dir_name"
lodelsites_data_dir="$instance_dir/$datas_dir_name"

echo "Creating multisite instance directory from template"
mkdir -pv $instance_dir
#Copy both EM for lodelsites and handled sites
cp -Rv $install_tpl/*.pickle "$instance_dir"
#Creating both conf directory
for dname in "lodelsites.conf.d" "server_conf.d"
do
	cp -Rv $install_tpl/$dname $instance_dir
	#make subst in configuration files
	for confname in $instance_dir/$dname/*
	do
		conf_file_subst $confname $name
	done
done
#Using monosite files to populate the instance directory
for fname in "Makefile" "lodel_admin.py"
do
	ln -vs $mono_model/$fname $instance_dir/$fname
done

#Dirty ln -s of plugins libdir
##@todo find another way to handles plugins in instances
ln -vs $libdir/plugins $instance_dir/plugins

#Dirty again :/
ln -vs $libdir/plugins/multisite/loader.py $instance_dir/

mkdir -pv "$lodelsites_ctx_dir"
mkdir -pv "$lodelsites_data_dir"
echo "Creating $lodelsites_ctx_dir/__init__.py"
> "$lodelsites_ctx_dir/__init__.py"


echo "Multisite $name created in $install_dir"
echo -e "Now you can :\ncd $instance_dir && make dyncode"
