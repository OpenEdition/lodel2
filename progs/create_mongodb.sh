#! /bin/bash

usage() {
	echo -e "Usage : $0 host port database newuser_identifier newuser_pwd (admin_identifier|config_file) [admin_pwd]" 1>&2
    echo -e "config_file has to define ADMIN and ADMINPWD" 1>&2
	exit 1
}

if [ $# -lt 6 ]
then
	echo "Not enough arguments" 1>&2
	usage
fi

if [ $# -eq 6 ]
then
    if [ ! -f $6 ]
    then  
	    echo "Not enough arguments or the configation file $6 doesn't exist" 1>&2
        usage
    else
	    . $6
    fi
fi

if [ $# -eq 7 ]
then
    ADMIN=$6
    ADMINPWD=$7
fi

host=$1
port=$2
db=$3
newuser=$4
newuserpwd=$5

mongo $1:$2/admin -u $ADMIN -p $ADMINPWD <<EOF
db.addUser('$4', '$5')
use $db
quit()
EOF