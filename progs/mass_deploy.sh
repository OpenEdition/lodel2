#!/bin/bash

if [ -f '/usr/share/dict/words' ]
then
	random_name=$(sed -nE 's/^([A-Za-z0-9]+)$/\1/p' /usr/share/dict/words |shuf|head -n1)
else
	random_name=$RANDOM
fi

if hash mongo 2>/dev/null
then
	echo "Mongo found"
else
	echo "You need mongo on this host to do a mass deploy !" >&2
	exit
fi

ninstance=$1
instance=${ninstance:=50}

echo -n "You are going to create $ninstance lodel2 instances. Are you sure ? Y/n "
read rep
if [ "$rep" = "Y" ]
then
	echo "GO ! (you have 3 secs to cancel)"
	sleep 3
else
	echo "You didn't answer 'Y' (yeah, case matter =P), exiting"
	exit
fi

echo "Creating instances"
for i in $(seq $ninstance)
do
	iname="${random_name}_$(printf "%05d" $i)"
	slim -n $iname -c
	slim -n $iname -s --interface web
	slim -n $iname -m
	slim -n $iname -s --datasource_connectors mongodb --host localhost --user lodel2 --password lodel2 --db_name $iname
	[@]LODEL2_PROGSDIR[@]/create_mongodb.sh localhost 27015 $iname lodel2 lodel2 [@]LODEL2_CONFDIR[@]/create_mongodb_config.cfg
done

