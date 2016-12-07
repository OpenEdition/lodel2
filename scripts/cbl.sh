#!/bin/bash
#
# CBL : Curl Benchmark on Lodel
#
# Usage : $0 [HOSTNAME] [INSTANCE_LIST_FILE] [N_CREATE] [N_EDIT] [N_DELETE]
#
# Instance_list_file is expected to be a file containing instances name (1 per
# line). Uses by default /tmp/lodel2_instance_list.txt
#
# Instances base URL are generated given the current webui implementation :
# http://HOST/INSTANCE_NAME/
#
#
# Scenario description :
#
# mass_creation instance_name iteration_count :
#	Create iteration_count time a random leobject in given instance_name
#	note : do note create relation between objects, only populate content
#	
#	step 1 : fetch all non abstract class name
# 	step 2 : loop on creation (using bash function curl_opt_create_CLSNAME)
#		that return the POST fields (populated with random values)
#
# mass_deletion instance_name iteration_count :
#	Foreach non asbtracty class delete iteration_count time an object of
#	current class in current instance
#
#	step 1 : fetch all non abstract class name
#	step 2 : loop on non abstract class name
#	step 3 : loop iteration_count time on deletion
#
# mass_link_edit instance_name iteration_count :
#	Foreach non abstract class make iteration_count time edition of an
#	object in current class
#	note : only implemented for Person for the moment
#	note : can maybe ask for invalid modifications
#
#	step 1 : fetch all non abstract class name
#	step 2 : loop on non abstract class name
#	step 3 : depends on curent class :
#		- fetch all existing id of current class
#		- fetch all existing id in class that can be linked with
#		  current class
#	step 4 : loop iteration_count time :
#		- choose a random id in current class
#		- choose random ids from linkable classes
#		- trigger edition using curl (with datas from the same
#		  bash function than creation : curl_opt_create_CLSNAME)
#
# Current way to run scenarios :
#
# using the function run_bg_with_param FUNCTION_NAME INSTANCE_LIST_FILE *ARGS
#
# The function name can be one of the scenario functions
# INSTANCE_LIST_FILE is the file containing instances list
# *ARGS are args given as it to FUNCTION_NAME after the instance_name argument
#
# function call : FUN_NAME INSTANCE_NAME *ARGS
#
# The run_bg_with_param run a scenario in background for each instance allowing
# to send a lot of request at the same time
#
#

usage() {
	echo "Usage : $0 [HOSTNAME] [INSTANCE_LIST_FILE] [CREATE_COUNT] [EDIT_COUNT] [DELETE_COUNT]"
	exit
}

host=$1
host=${host:=localhost}
instance_list=$2
instance_list=${instance_list:=/tmp/lodel2_instance_list.txt}
#A modifier for requests count
n_create=$3
n_create=${n_create:=50}
n_edit=$4
n_edit=${n_edit:=10}
n_delete=$5
n_delete=${n_delete:=10}

for i in $(seq $#)
do
	echo $1 |grep -E "^-?-h" &>/dev/null
	shift
done


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
	cls_list_file=$(fetch_all_classes $1)

	if [ -z "$(cat $cls_list_file)" ]
	then
		echo "Failed to fetch class list for instance $1. Abording..." >&2
		exit
	fi

	if [ "$iteration_count" -le "0" ]
	then
		return
	fi

	for i in $(seq $iteration_count)
	do
		cls=$(shuf -n1 $cls_list_file)
		echo "${base_uri}$(uri_create $cls) POST $(curl_opt_create_$cls)"
	done
	rm -v $cls_list_file >&2
}

mass_link_edit() {
	#mass linking & edition scenarion
	#$1 is instance name
	#$2 is iteration count
	instance_name=$1
	iteration_count=$2
	base_uri=$(_base_uri $1)
	cls_list_file=$(fetch_all_classes $1)

	for cls in $(cat $cls_list_file)
	do
		case $cls in
			Person)
				person_ids=$(fetch_all_ids $1 Person)
				section_ids=$(fetch_all_ids $1 Section)
				subsection_ids=$(fetch_all_ids $1 Subsection)
				text_ids=$($cmktemp)
				cat $section_ids $subsection_ids | shuf > $text_ids
				for i in $(seq $iteration_count)
				do
					cur_id=$(shuf -n1 $person_ids)
					alias_count=$(shuf -i1-5 -n1)
					ltext_count=$(shuf -i1-5 -n1)
					alias_param=$(head -n $(expr $alias_count \* $i) $person_ids| tail -n$alias_count|tr -s "\n" "," | sed 's/,$//')
					txt_param=$(head -n $(expr $ltext_count \* $i) $text_ids | tail -n$ltext_count|tr -s "\n" "," | sed 's/,$//')
					echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $alias_param $txt_param)&uid=$cur_id"
				done
				rm -v $text_ids $person_ids $section_ids $subsection_ids
				;;
            
            Collection)
                collections_ids=$(fetch_all_ids $1 Collection)
                publication_ids=$(fetch_all_ids $1 Publication)
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $collections_ids)
                    publications_count=$(shuf -i1-5 -n1)
                    publication_param=$(head -n $(expr $publications_count \* $i) $publication_ids| tail -n$publications_count|tr -s "\n" ",")
		    echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $publication_param)&uid=$cur_id"
                done
                rm -v $collections_ids $publication_ids
                ;;

            Publication)
                publication_ids=$(fetch_all_ids $1 Publication)
                collection_ids=$(fetch_all_ids $1 Collection)
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $publication_ids)
                    collections_count=$(shuf -i1-5 -n1)
                    collection_param=$(head -n $(expr $collections_count \* $i) $collection_ids| tail -n$collections_count|tr -s "\n" ",")
		    echo "$base_uri/admin.update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $collection_param)&uid=$cur_id"
                done
                rm -v $publication_ids $collection_ids >&2
                ;;
			
			Section)
                section_ids=$(fetch_all_ids $1 Section)
                child_ids=$(fetch_all_ids $1 Subsection)
                person_ids=$(fetch_all_ids $1 Person)
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $section_ids)
                    child_count=$(shuf -i1-5 -n1)
                    person_count=$(shuf -i1-5 -n1)
                    child_param=$(head -n $(expr $child_count \* $i) $child_ids| tail -n$child_count|tr -s "\n" ",")
                    person_param=$(head -n $(expr $person_count \* $i) $person_ids| tail -n$person_count|tr -s "\n" ",")
		    echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $child_param $person_param)&uid=$cur_id"
                done
                rm -v $section_ids $child_ids $person_ids >&2
                ;;
                
            Subsection)
                subsection_ids=$(fetch_all_ids $1 Subsection)
                section_ids=$(fetch_all_ids $1 Section)
                persons_ids=$(fetch_all_ids $1 Person)
                parent_ids=$($cmktemp)
                cat $section_ids $subsection_ids | shuf > $parent_ids
                child_ids=$subsection_ids
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $subsection_ids)
                    child_count=$(shuf -i1-5 -n1)
                    parent_count=$(shuf -i1-5 -n1)
                    person_count=$(shuf -i1-5 -n1)
                    child_param=$(head -n $(expr $child_count \* $i) $child_ids| tail -n$child_count|tr -s "\n" ",")
                    parent_param=$(head -n $(expr $parent_count \* $i) $parent_ids| tail -n$parent_count|tr -s "\n" ",")
                    person_param=$(head -n $(expr $person_count \* $i) $persons_ids| tail -n$person_count|tr -s "\n" ",")
		    echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $child_param $person_param $parent_param)&uid=$cur_id"
                done
                rm -v $subsection_ids $parent_ids $section_ids $persons_ids >&2
                ;;
			*)
				;;
			
		esac
	done
	rm -v $cls_list_file >&2
}

mass_deletion() {
	#mass deletion scenario
	#$1 is instance name
	#$2 number of deletion per classes !
	instance_name=$1
	iteration_count=$2
	base_uri=$(_base_uri $1)
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
			echo "${base_uri}/admin/delete?classname=$cls&lodel_id=$id"
		done
		rm -v $id_list_file
	done
	rm -v $cls_list_file
}


fetch_all_classes() {
	#$1 is intance name
	cls_list_file=$($cmktemp)
	$curl_raw "$(_base_uri $1)/list_classes" | grep -v Abstract |sed -nE 's/^ *<li> +<a href="show_class([^"]+)".*$/\1/p'|cut -d"=" -f2 > $cls_list_file
	if [ -z "$(cat $cls_list_file)" ]
	then
		echo "Unable to fetch class list for $1" >&2
		echo "Request was : $curl_raw '$(_base_uri $1)/list_classes'" >&2
		rm $cls_list_file
		exit 1
	fi
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
		sleep 1
	done
	for pid in $(cat $pidlist)
	do
		wait $pid
	done
	rm -v $pidlist
}

get_queries_with_params() {
	#$1 is the function name to run
	#$2 is the instance_list filename
	#other parameters are given to the function
	fun=$1
	instance_list=$2
	shift;shift
	counter=0
	for iname in $(cat $instance_list| sort)
	do
		echo "Running $fun $iname $@" >&2
		beg=$(date "+%s")
		$fun $iname $@
		tsecs=$(expr $(date "+%s") - $beg)
		left=$(expr $(cat $instance_list |wc -l) - $counter)
		counter=$(expr $counter + 1)
		tleft=$(expr $left \* $tsecs)
		percent_done=$(echo "2k ${counter}.0 100.0 * $(cat $instance_list |wc -l).0 2k/ f" | dc)
		echo -e "Done in ${tsecs}s\t$fun ${percent_done}% done ~$tleft secs" >&2

	done | shuf
}

get_queries_with_params "mass_creation" $instance_list $n_create
get_queries_with_params "mass_link_edit" $instance_list $n_edit
get_queries_with_params "mass_deletion" $instance_list $n_delete

