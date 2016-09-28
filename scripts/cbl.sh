#!/bin/bash

usage() {
	echo "Usage : $0 [HOST] [INSTANCE_LIST_FILE]"
	exit
}

host=$1
host=${host:=localhost}
instance_list=$2
instance_list=${instance_list:=/tmp/lodel2_instance_list.txt}


logdir="/tmp/lodel2_cbl_logs"
if [ -d "$logdir" ]
then
	echo "WARNING : $logdir allready exists. It's a better idea to delete it before running this script again"
	echo "waiting 3s"
	sleep 3
fi
mkdir -p $logdir

random_word_file="/usr/share/dict/words"

#curl_options='--silent -o /dev/null -s -w %{http_code}:%{time_connect}:%{time_starttransfer}:%{time_total}\n'
curl_options='--silent -o /dev/null -s -w %{url_effective};%{http_code};%{time_connect};%{time_starttransfer};%{time_total}\n'
curl_debug_opt='-v -w %{url_effective};%{http_code};%{time_connect};%{time_starttransfer};%{time_total}\n'
curl_cmd="curl $curl_options"
curl_raw="curl --silent"
curl_debug="curl $curl_debug_opt"

curcurl="$curl_cmd"

cmktemp="mktemp -t lodel2_cbl_XXXXXXXX"

_base_uri() {
	echo -n "http://$host/$1"
}

rnd_str() {
	len=$1
	cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $len | head -n 1
}

rnd_str_len() {
	minlen=$1
	maxlen=$2
	cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $(shuf -i${minlen}-${maxlen} -n1) | head -n 1
}

mass_creation() {
	#mass creation scenario
	#$1 is instance name
	#$2 is iteration count (1 iteration is 1 creation of a random class)
	instance_name=$1
	iteration_count=$2
	base_uri=$(_base_uri $1)
	logfile="$logdir/mass_creation_${instance_name}.log"
	cls_list_file=$(fetch_all_classes $1)

	for i in $(seq $iteration_count)
	do
		cls=$(shuf -n1 $cls_list_file)
		$curcurl -d "$(curl_opt_create_$cls)" "${base_uri}$(uri_create $cls)" | tee -a $logfile
	done

	rm -v $cls_list_file
}

mass_link_edit() {
	#mass linking & edition scenarion
	#$1 is instance name
	#$2 is iteration count
	instance_name=$1
	iteration_count=$2
	base_uri=$(_base_uri $1)
	logfile="$logdir/mass_link_edit_${instance_name}.log"
	cls_list_file=$(fetch_all_classes $1)

	for cls in $(cat $cls_list_file)
	do
		case $cls in
			Person)
				person_ids=$(fetch_all_ids $1 Person)
				section_ids=$(fetch_all_ids $1 Section)
				subsection_ids=$(fetch_all_ids $1 Section)
				text_ids=$($cmktemp)
				cat $section_ids $subsection_ids | shuf > $text_ids
				for i in $(seq $iteration_count)
				do
					cur_id=$(shuf -n1 $person_ids)
					alias_count=$(shuf -i1-5 -n1)
					ltext_count=$(shuf -i1-5 -n1)
					alias_param=$(head -n $(expr $alias_count \* $i) $person_ids| tail -n$alias_count|tr -s "\n" ",")
					txt_param=$(head -n $(expr $ltext_count \* $i) $text_ids | tail -n$ltext_count|tr -s "\n" ",")
					$curcurl -d "$(curl_opt_create_$cls $alias_param $txt_param)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
				done
				rm -v $text_ids $person_ids $section_ids $subsection_ids
				;;

			*)
				;;
			
		esac
	done
	rm -v $cls_list_file
}

mass_deletion() {
	#mass deletion scenario
	#$1 is instance name
	#$2 number of deletion per classes !
	instance_name=$1
	iteration_count=$2
	base_uri=$(_base_uri $1)
	logfile="$logdir/mass_deletion_${instance_name}.log"
	cls_list_file=$(fetch_all_classes $1)
	
	for cls in $(cat $cls_list_file)
	do
		id_list_file=$(fetch_all_ids $1 $cls)
		if [ "$iteration_count" -gt "$(wc -l $id_list_file | cut -d " " -f1)" ]
		then
			max_iter=$(wc -l $id_list_file | cut -d " " -f1)
		else
			max_iter="$iteration_count"
		fi

		for i in $(seq $max_iter)
		do
			id=$(tail -n $i $id_list_file | head -n1)
			$curcurl "${base_uri}/admin/delete?classname=$cls&lodel_id=$id" | tee -a $logfile
		done
		rm -v $id_list_file
	done
	rm -v $cls_list_file
}


fetch_all_classes() {
	#$1 is intance name
	cls_list_file=$($cmktemp)
	$curl_raw "$(_base_uri $1)/list_classes" | grep -v Abstract |sed -nE 's/^ *<li> +<a href="([^"]+)" target="_blank".*$/\1/p'|cut -d"=" -f2 > $cls_list_file
	echo $cls_list_file
}

fetch_all_ids() {
	# Fetch all ids of a class in an instance and shuffle them
	instance_name=$1
	classname=$2
	idfile=$($cmktemp)
	$curl_raw "$(_base_uri $1)/show_class?classname=$2" | sed -nE 's/^.*<li><a href="[^=]+=[^=]+=([0-9]+)".*$/\1/p' |shuf > $idfile
	echo $idfile
}

uri_create() {
	clsname=$1
	echo -n "/admin/create?classname=$1"
}

curl_opt_create_Person() {
	#$1 is alias id
	#$2 is linked_texts id (comma separated)
	echo "field_input_lastname=$(rnd_str_len 10 20)&field_input_firstname=$(rnd_str_len 10 20)&field_input_alias=$1&field_input_linked_texts=$2&classname=Person"
}

curl_opt_create_User() {
	echo "field_input_lastname=$(rnd_str_len 10 20)&field_input_firstname=$(rnd_str_len 10 20)&field_input_password=$(rnd_str 50)&field_input_login=$(rnd_str_len 5 20)&classname=User"
}

curl_opt_create_Collection() {
	#$1 is publications id (comma separated)
	echo "field_input_title=$(rnd_str_len 20 50)&field_input_publications=$1&classname=Collection"
}

curl_opt_create_Publication() {
	#$1 collections id comma separated
	echo "field_input_collection=$1&classname=Publication"
}

curl_opt_create_Section() {
	#$1 childs id (comma separated)
	#$2 linked_persons id (comma separated)
	echo "field_input_title=$(rnd_str_len 20 50)&field_input_subtitle=$(rnd_str_len 20 50)&field_input_childs=$1&field_input_linked_persons=$2&classname=Section"
}

curl_opt_create_Subsection() {
	#$1 childs id (comma separated)
	#$2 linked_persons id (comma separated)
	#$3 parants id (comma separated)
	echo "field_input_title=$(rnd_str_len 20 50)&field_input_subtitle=$(rnd_str_len 20 50)&field_input_childs=$1&field_input_linked_persons=$2&field_input_parent=$3&classname=Subsection"
}

run_bg_with_param() {
	#$1 is the function name to run
	#$2 is the instance_list filename
	#other parameters are given to the function
	fun=$1
	instance_list=$2
	shift;shift

	pidlist=$($cmktemp)
	for iname in $(cat $instance_list)
	do
		$fun $iname $@ &
		echo $! >> $pidlist
	done
	for pid in $(cat $pidlist)
	do
		wait $pid
	done
	rm -v $pidlist
}

run_bg_with_param "mass_creation" $instance_list 50
run_bg_with_param "mass_link_edit" $instance_list 10
run_bg_with_param "mass_deletion" $instance_list 10

echo ""
echo "Logs can be found in $logdir"

