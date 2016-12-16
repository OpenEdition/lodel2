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
logdir="/tmp/lodel2_cbl_logs"
if [ -d "$logdir" ]
then
	echo "WARNING : $logdir allready exists. It's a better idea to delete it before running this script again"
	echo "waiting 3s"
	sleep 3
fi
mkdir -p $logdir

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

rnd_date() {
    M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
    JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28'  | head -n 1)
    AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
    echo -n "$AA-$M-$JJ"
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
        $curcurl -d "$(curl_opt_create_$cls)" "${base_uri}$(uri_create $cls)" | tee -a $logfile
		# echo "${base_uri}$(uri_create $cls) POST $(curl_opt_create_$cls)"
	done
	rm -v $cls_list_file >&2
}

mass_link_edit() {
	#mass linking & edition scenario
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
            Entry)
                entries_ids=$(fetch_all_ids $1 Entry)
                articles_ids=$(fetch_all_ids $1 Article)
				reviews_ids=$(fetch_all_ids $1 Review)
				text_ids=$($cmktemp)
				cat $articles_ids $reviews_ids | shuf > $text_ids
				for i in $(seq $iteration_count)
				do
					cur_id=$(shuf -n1 $entries_ids)
					ltext_count=$(shuf -i1-5 -n1)
					txt_param=$(head -n $(expr $ltext_count \* $i) $text_ids | tail -n$ltext_count|tr -s "\n" "," | sed 's/,$//')
					role=$(shuf -e 'geography' 'subject' | head -n 1)
					$curcurl -d "$(curl_opt_create_$cls  $txt_param $role)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
                    #echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $txt_param $role)&uid=$cur_id"| tee -a $logfile
				done
				rm -v $text_ids $entries_ids $reviews_ids $articles_ids
				;;
                
			Person)
				person_ids=$(fetch_all_ids $1 Person)
				issues_ids=$(fetch_all_ids $1 Issue)
				parts_ids=$(fetch_all_ids $1 Part)
				publication_ids=$($cmktemp)
				cat $issues_ids $parts_ids | shuf > $publication_ids
                articles_ids=$(fetch_all_ids $1 Article)
				reviews_ids=$(fetch_all_ids $1 Review)
				text_ids=$($cmktemp)
				cat $articles_ids $reviews_ids | shuf > $text_ids
				for i in $(seq $iteration_count)
				do
					cur_id=$(shuf -n1 $person_ids)
					pub_count=$(shuf -i1-5 -n1)
					ltext_count=$(shuf -i1-5 -n1)
					pub_param=$(head -n $(expr $ltext_count \* $i) $publication_ids | tail -n$pub_count|tr -s "\n" "," | sed 's/,$//')
					txt_param=$(head -n $(expr $ltext_count \* $i) $text_ids | tail -n$ltext_count|tr -s "\n" "," | sed 's/,$//')
                    $curcurl -d "$(curl_opt_create_$cls  $txt_param $pub_param)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
					#echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $txt_param $pub_param)&uid=$cur_id"
				done
				rm -v $parts_ids $text_ids $person_ids $issues_ids $reviews_ids $articles_ids $publication_ids
				;;
            
            Collection)
                collections_ids=$(fetch_all_ids $1 Collection)
                issues_ids=$(fetch_all_ids $1 Issue)
                persons_ids=$(fetch_all_ids $1 Person)
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $collections_ids)
                    publications_count=$(shuf -i1-5 -n1)
                    persons_count=$(shuf -i1-5 -n1)
                    publication_param=$(head -n $(expr $publications_count \* $i) $issues_ids| tail -n$publications_count|tr -s "\n" ",")
                    person_param=$(head -n $(expr $persons_count \* $i) $persons_ids| tail -n$persons_count|tr -s "\n" ",")
                    $curcurl -d "$(curl_opt_create_$cls $person_param $publication_param)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
		            #echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $person_param $publication_param)&uid=$cur_id"
                done
                rm -v $collections_ids $issues_ids $persons_ids
                ;;

            Issue)
                issues_ids=$(fetch_all_ids $1 Issue)
                parts_ids=$(fetch_all_ids $1 Part)
                collection_ids=$(fetch_all_ids $1 Collection)
                persons_ids=$(fetch_all_ids $1 Person)
                reviews_ids=$(fetch_all_ids $1 Review)
                articles_ids=$(fetch_all_ids $1 Article)
                text_ids=$($cmktemp)
				cat $articles_ids $reviews_ids | shuf > $text_ids
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $issues_ids)
                    collections_count=1
                    collection_param=$(head -n $(expr $collections_count \* $i) $collection_ids| tail -n$collections_count|tr -s "\n")
                    persons_count=$(shuf -i1-5 -n1)
                    person_param=$(head -n $(expr $persons_count \* $i) $persons_ids| tail -n$persons_count|tr -s "\n" ",")
                    parts_count=$(shuf -i1-5 -n1)
                    parts_param=$(head -n $(expr $parts_count \* $i) $parts_ids| tail -n$parts_count|tr -s "\n" ",")
                    ltext_count=$(shuf -i1-5 -n1)
                    txt_param=$(head -n $(expr $ltext_count \* $i) $text_ids | tail -n$ltext_count|tr -s "\n" "," | sed 's/,$//')
                    $curcurl -d "$(curl_opt_create_$cls $person_param $collection_param $parts_param $txt_param)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
		            #echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $person_param $collection_param $parts_param)&uid=$cur_id"
                done
                rm -v $persons_ids $collection_ids $issues_ids $parts_ids $reviews_ids $articles_ids $text_ids >&2
                ;;
			
			Part)
                issues_ids=$(fetch_all_ids $1 Issue)
                parts_ids=$(fetch_all_ids $1 Part)
                containers_ids=$($cmktemp)
				cat $issues_ids $parts_ids | shuf > $containers_ids
                person_ids=$(fetch_all_ids $1 Person)
                reviews_ids=$(fetch_all_ids $1 Review)
                articles_ids=$(fetch_all_ids $1 Article)
                text_ids=$($cmktemp)
				cat $articles_ids $reviews_ids | shuf > $text_ids
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $parts_ids)
                    container_count=1
                    person_count=$(shuf -i1-5 -n1)
                    container_param=$(head -n $(expr $container_count \* $i) $containers_ids| tail -n$container_count|tr -s "\n")
                    person_param=$(head -n $(expr $person_count \* $i) $person_ids| tail -n$person_count|tr -s "\n" ",")
                    ltext_count=$(shuf -i1-5 -n1)
                    txt_param=$(head -n $(expr $ltext_count \* $i) $text_ids | tail -n$ltext_count|tr -s "\n" "," | sed 's/,$//')
                    linked_part=''
                    $curcurl -d "$(curl_opt_create_$cls $person_param $container_param $linked_part $txt_param)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
		            #echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $person_param $container_param $linked_part $txt_param)&uid=$cur_id"
                done
                rm -v $containers_ids $text_ids $person_ids $issues_ids $parts_ids $reviews_ids $articles_ids >&2
                ;;
                
            Article)
                articles_ids=$(fetch_all_ids $1 Article)
                entries_ids=$(fetch_all_ids $1 Entry)
                issues_ids=$(fetch_all_ids $1 Issue)
                parts_ids=$(fetch_all_ids $1 Part)
                containers_ids=$($cmktemp)
				cat $issues_ids $parts_ids | shuf > $containers_ids
                persons_ids=$(fetch_all_ids $1 Person)
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $articles_ids)
                    entries_count=$(shuf -i1-10 -n1)
                    containers_count=1
                    person_count=$(shuf -i1-5 -n1)
                    entries_param=$(head -n $(expr $entries_count \* $i) $entries_ids| tail -n$entries_count|tr -s "\n" ",")
                    container_param=$(head -n $(expr $containers_count \* $i) $containers_ids| tail -n$containers_count|tr -s "\n")
                    person_param=$(head -n $(expr $person_count \* $i) $persons_ids| tail -n$person_count|tr -s "\n" ",")
                    $curcurl -d "$(curl_opt_create_$cls $entries_param $person_param $container_param)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
		            #echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $entries_param $person_param $container_param)&uid=$cur_id"
                done
                rm -v $articles_ids $entries_ids $issues_ids $persons_ids $parts_ids $containers_ids >&2
                ;;
                
            Review)
                reviews_ids=$(fetch_all_ids $1 Review)
                entries_ids=$(fetch_all_ids $1 Entry)
                issues_id=$(fetch_all_ids $1 Issue)
                parts_id=$(fetch_all_ids $1 Part)
                containers_ids=$($cmktemp)
				cat $issues_id $parts_id | shuf > $containers_ids
                persons_ids=$(fetch_all_ids $1 Person)
                for i in $(seq $iteration_count)
                do
                    cur_id=$(shuf -n1 $reviews_ids)
                    entries_count=$(shuf -i1-10 -n1)
                    containers_count=1
                    person_count=$(shuf -i1-5 -n1)
                    entries_param=$(head -n $(expr $entries_count \* $i) $entries_ids| tail -n$entries_count|tr -s "\n" ",")
                    container_param=$(head -n $(expr $containers_count \* $i) $containers_ids| tail -n$containers_count|tr -s "\n")
                    person_param=$(head -n $(expr $person_count \* $i) $persons_ids| tail -n$person_count|tr -s "\n" ",")
                    $curcurl -d "$(curl_opt_create_$cls $entries_param $person_param $container_param)&uid=$cur_id" "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id" | tee -a $logfile
		            #echo "$base_uri/admin/update?classname=$cls&lodel_id=$cur_id POST $(curl_opt_create_$cls $entries_param $person_param $container_param)&uid=$cur_id"
                done
                rm -v $reviews_ids $entries_ids $issues_id $persons_ids $parts_id $containers_ids >&2
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
			#echo "${base_uri}/admin/delete?classname=$cls&lodel_id=$id"
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
	#$1 is linked_texts ids (comma separated)
	#$2 is containers ids(comma separated)
	echo "field_input_lastname=$(rnd_str_len 10 20)&field_input_firstname=$(rnd_str_len 10 20)&field_input_linked_texts=$1&field_input_linked_containers=$2&classname=Person"
}

curl_opt_create_User() {
	echo "field_input_lastname=$(rnd_str_len 10 20)&field_input_firstname=$(rnd_str_len 10 20)&field_input_password=$(rnd_str 50)&field_input_login=$(rnd_str_len 5 20)&classname=User"
}
curl_opt_create_Entry() {
    #$1 texts ids, separated by comma
    #$2 string
	echo "field_input_linked_texts=$1&field_input_name=$(rnd_str_len 10 20)&field_input_role=$2&field_input_description=$(rnd_str_len 100 500)&classname=Entry"
}

curl_opt_create_Collection() {
    #$1 is persons ids, separated by comma
    #$2 is issues ids, separated by comma
    issn=$(</dev/urandom tr -dc 0-9 | head -c8;echo;)
    lg=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
	echo "field_input_title=$(rnd_str_len 20 100)&field_input_subtitle=$(rnd_str_len 20 100)&field_input_language=$lg&field_input_linked_directors=$1&field_input_linked_issues=$2&field_input_description=$(rnd_str_len 100 500)&field_input_publisher_note=$(rnd_str_len 100 500)&field_input_issn=$issn&classname=Collection"
}

curl_opt_create_Issue() {
    #$1 persons ids, separated by comma
    #$2 collection id
    #$3 parts ids, separated by comma
    #$4 texts ids, separated by comma
    lg=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
    isbn=$(</dev/urandom tr -dc 0-9 | head -c10;echo;)
    pisbn=$(</dev/urandom tr -dc 0-9 | head -c10;echo;)
	echo "field_input_title=$(rnd_str_len 20 100)&field_input_subtitle=$(rnd_str_len 20 100)&field_input_language=$lg&field_input_linked_directors=$1&field_input_description=$(rnd_str_len 100 500)&field_input_publisher_note=$(rnd_str_len 100 500)&field_input_isbn=$isbn&field_input_print_isbn=$pisbn&field_input_number=$(rnd_str_len 10 50)&field_input_cover=$(rnd_str_len 20 50)&field_input_print_pub_date=$(rnd_date)&field_input_e_pub_date=$(rnd_date)&field_input_abstract=$(rnd_str_len 5000 20000)&field_input_collection=$2&field_input_linked_parts=$3&field_input_linked_texts=$4&classname=Issue"
}

curl_opt_create_Part() {
    #$1 persons ids, separated by comma
    #$2 publication id (issue id or part id)
    #$3 parts ids, separated by comma
    #$4 text ids, separated by comma
    lg=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
	echo "field_input_title=$(rnd_str_len 20 100)&field_input_subtitle=$(rnd_str_len 20 100)&field_input_language=$lg&field_input_linked_directors=$1&field_input_description=$(rnd_str_len 100 500)&field_input_publisher_note=$(rnd_str_len 100 500)&field_input_publication=$2&field_input_linked_parts=$3&field_input_linked_texts=$4&classname=Part"
}

curl_opt_create_Article() {
	#$1 entries ids (comma separated)
	#$2 linked_persons ids (comma separated)
	#$3 container id
    lg=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
	echo "field_input_title=$(rnd_str_len 20 100)&field_input_linked_entries=$1&field_input_linked_persons=$2&field_input_linked_container=$3&field_input_subtitle=$(rnd_str_len 20 100)&field_input_language=$lg&field_input_text=$(rnd_str_len 10000 50000)&field_input_pub_date=$(rnd_date)&field_input_footnotes=$(rnd_str_len 5000 20000)&field_input_abstract=$(rnd_str_len 1000 5000)&field_input_appendix=$(rnd_str_len 5000 20000)&field_input_bibliography=$(rnd_str_len 5000 20000)&field_input_author_note=$(rnd_str_len 5000 20000)&classname=Article"
}

curl_opt_create_Review() {
	#$1 entries ids (comma separated)
	#$2 linked_persons ids (comma separated)
	#$3 container id
    lg=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
	echo "field_input_title=$(rnd_str_len 20 50)&field_input_subtitle=$(rnd_str_len 20 50)&field_input_language=$lg&field_input_text=$(rnd_str_len 10000 50000)&field_input_pub_date=$(rnd_date)&field_input_footnotes=$(rnd_str_len 5000 20000)&field_input_linked_entries=$1&field_input_linked_persons=$2&field_input_linked_container=$3&field_input_reference=$(rnd_str_len 5000 20000)&classname=Review"
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

#run_bg_with_param "mass_creation" $instance_list $n_create
#run_bg_with_param "mass_link_edit" $instance_list $n_edit
#run_bg_with_param "mass_deletion" $instance_list $n_delete

#get_queries_with_params "mass_creation" $instance_list $n_create
get_queries_with_params "mass_link_edit" $instance_list $n_edit
#get_queries_with_params "mass_deletion" $instance_list $n_delete
