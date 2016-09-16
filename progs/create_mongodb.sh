#! /bin/bash

usage() {
	echo -e "Usage : $0 host database newuser_identifier newuser_pwd (admin_identifier|config_file) [admin_pwd]" 1>&2
    echo -e "config_file has to define ADMIN and ADMINPWD" 1>&2
	exit 1
}

if [ $# -lt 5 ]
then
	echo "Not enough arguments" 1>&2
	usage
fi

if [ $# -eq 5 ]
then
    if [ ! -f $5 ]
    then  
	    echo "Not enough arguments or the configation file $5 doesn't exist" 1>&2
        usage
    else
	    . $5
    fi
fi

if [ $# -eq 6 ]
then
    ADMIN=$5
    ADMINPWD=$6
fi

host=$1
db=$2
newuser=$3
newuserpwd=$4

mongo $1/admin -u $ADMIN -p $ADMINPWD <<EOF
db.addUser('$3', '$4')
use $db
quit()
EOF
