#!/bin/bash

host=$1
instance=$2
N=$3
HOSTDB=localhost

M=$(expr $N / 10)
for i in `eval echo {1..$M}`;
do
    COLPUBLI=""
    COLT=$(lenmax=100;wcount=5; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
    curl -A "Mozilla/5.0" -L -s -d "field_input_title=$COLT&field_input_publications=$COLPUBLI&classname=Collection" http://$host/$instance/admin/create?classname=Collection
    ITTHM="themetest"
    ITNAME=$(lenmax=30;wcount=3; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    ITVAL=$(lenmax=10;wcount=1; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    curl -A "Mozilla/5.0" -L -s -d "field_input_theme=$ITTHM&field_input_name=$ITNAME&field_input_value=$ITVAL&classname=Indextheme" http://$host/$instance/admin/create?classname=Indextheme
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
    res=$(printf "use lodel2_$instance\n db.Indextheme.find({}, {lodel_id:1, _id:0}).limit(5)" | mongo  $HOSTDB/admin -u lodel2_admin -p lapwd  | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d")
    tmp=""
    for i in $res
    do
        if [[ ! -z $tmp ]]
        then
            tmp=$(printf "$tmp, $i")
        else
            tmp=$i
        fi
    done
    SECIND=$tmp
    SECTTL=$(lenmax=60;wcount=5; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    curl -A "Mozilla/5.0" -L -s -d "field_input_linked_persons=$SECLP&field_input_subtitle=$SECST&field_input_indexes=$SECIND&field_input_title=$SECTTL&classname=Section" http://$host/$instance/admin/create?classname=Section
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
    res=$(printf "use lodel2_$instance\n db.Indextheme.find({}, {lodel_id:1, _id:0}).limit(3)" | mongo  $HOSTDB/admin -u lodel2_admin -p lapwd  | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d")
    tmp=""
    for i in $res
    do
        if [[ ! -z $tmp ]]
        then
            tmp=$(printf "$tmp, $i")
        else
            tmp=$i
        fi    
    SSSECIND=$tmp
    SSSECTTL=$(lenmax=60;wcount=5; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    res=$(printf "use lodel2_$instance\n db.Collection.find({}, {lodel_id:1, _id:0}).limit\(1\)" | mongo  $HOSTDB/admin -u lodel2_admin -p lapwd  | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d")
    PUBCOLLS=$res
    curl -A "Mozilla/5.0" -L -s -d "field_input_linked_persons=$SSSECLP&field_input_subtitle=$SSSECST&field_input_parent=$SSSECPAR&field_input_indexes=$SSSECIND&field_input_title=$SSSECTTL&classname=Subsection" http://$host/$instance/admin/create?classname=Subsection
    curl -A "Mozilla/5.0" -L -s -d "field_input_collection=$PUBCOLLS&classname=Publication" http://$host/$instance/admin/create?classname=Publication
done