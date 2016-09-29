#!/bin/bash

usage() {
	echo -e "Usage : $0 host_of_server instance_name host_of_db number_of_iterations >&2
	echo -e "Example : create_datas locahost instance_00001 localhost:28015 1000"
	echo -e "Example : create_datas locahost instance_00001 localhost 1000"
	exit 1
}

if [ $# -lt 3 ]
then
	echo "Not enough arguments" >&2
	usage
fi

host=$1
instance=$2
N=$4
HOSTDB=$3

M=$(expr $N / 10)
for i in `eval echo {1..$M}`;
do
    COLPUBLI=""
    COLT=$(lenmax=100;wcount=5; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
    curl -A "Mozilla/5.0" -L -s -d "field_input_title=$COLT&field_input_publications=$COLPUBLI&classname=Collection" http://$host/$instance/admin/create?classname=Collection
    LN=$(lenmax=20;wcount=1; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    FN=$(lenmax=20;wcount=1; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    curl -A "Mozilla/5.0" -L -s -d "field_input_lastname=$LN&field_input_firstname=$FN&classname=Person" http://$host/$instance/admin/create?classname=Person
    PWD='pwgen 10'
    LOGIN="${FN,,}$(printf "%d" $RANDOM)"
    curl -A "Mozilla/5.0" -L -s -d "field_input_lastname=$LN&field_input_firstname=$FN&field_input_password=$PWD&field_input_login=$LOGIN&classname=User" http://$host/$instance/admin/create?classname=User
done

M=$(expr $N / 4)
for i in `eval echo {1..$M}`;
do
    persons=$(printf "use lodel2_$instance\n db.Person.find({}, {lodel_id:1, _id:0}).limit(3)" | mongo  $HOSTDB/admin -u lodel2_admin -p lapwd | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d")
    tmp=""
    for i in $persons
    do
        if [[ ! -z $tmp ]]
        then
            tmp=$(printf "$tmp, $i")
        else
            tmp=$i
        fi
    done
    SECLP=$tmp
    SECST=$(lenmax=60;wcount=10; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    SECTTL=$(lenmax=60;wcount=5; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    curl -A "Mozilla/5.0" -L -s -d "field_input_linked_persons=$SECLP&field_input_subtitle=$SECSTD&field_input_title=$SECTTL&classname=Section" http://$host/$instance/admin/create?classname=Section
done

for i in `eval echo {1..$N}`;
do
    persons=$(printf "use lodel2_$instance\n db.Person.find({}, {lodel_id:1, _id:0}).limit(3)" | mongo  $HOSTDB/admin -u lodel2_admin -p lapwd  | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d")
    for i in $persons
    do
        if [[ ! -z $tmp ]]
        then
            tmp=$(printf "$tmp, $i")
        else
            tmp=$i
        fi
    done
    SSSECLP=$tmp
    SSSECST=$(lenmax=60;wcount=10; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    res=$(printf "use lodel2_$instance\n db.Section.find({}, {lodel_id:1, _id:0}).limit(1)" | mongo  $HOSTDB/admin -u lodel2_admin -p lapwd  | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d")
    SSSECPAR=$res
    SSSECTTL=$(lenmax=60;wcount=5; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    res=$(printf "use lodel2_$instance\n db.Collection.find({}, {lodel_id:1, _id:0}).limit(1)" | mongo  $HOSTDB/admin -u lodel2_admin -p lapwd  | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d")
    PUBCOLLS=$res
    curl -A "Mozilla/5.0" -L -s -d "field_input_linked_persons=$SSSECLP&field_input_subtitle=$SSSECST&field_input_parent=$SSSECPAR&field_input_title=$SSSECTTL&classname=Subsection" http://$host/$instance/admin/create?classname=Subsection
    curl -A "Mozilla/5.0" -L -s -d "field_input_collection=$PUBCOLLS&classname=Publication" http://$host/$instance/admin/create?classname=Publication
done
