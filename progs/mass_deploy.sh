#!/bin/bash

if [ -f '/usr/share/dict/words' ]
then
	random_name=$(sed -nE 's/^([A-Za-z0-9]+)$/\1/p' /usr/share/dict/words |shuf|head -n1)
else
	random_name=$RANDOM
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
done

