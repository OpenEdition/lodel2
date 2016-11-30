#!/bin/bash

usage() {
	echo -e "Usage : $0 host_of_server instance_name host_of_db number_of_iterations >&2"
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
dbname=lodel2_$instance
dbuser=admin 
dbpwd=pass

M=$(($N*20))
for i in `eval echo {1..$M}`;
do
    # Classe Person
    LN=$(lenmax=20;wcount=1; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    FN=$(lenmax=20;wcount=1; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    $LC=''
    curl -A "Mozilla/5.0" -L -s -d "field_input_lastname=$LN&field_input_firstname=$FN&field_input_linked_containers=$LC&classname=Person" http://$host/$instance/admin/create?classname=Person
    
    # Classe User
    PWD='pwgen 10'
    LOGIN="${FN,,}$(printf "%d" $RANDOM)"
    curl -A "Mozilla/5.0" -L -s -d "field_input_lastname=$LN&field_input_firstname=$FN&field_input_password=$PWD&field_input_login=$LOGIN&classname=User" http://$host/$instance/admin/create?classname=User
    
    # Classe Entry, champs à remplir : name, description, role, linked_texts
    ENLT='' #$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Article.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | shuf | head -n 3; )
    ENROLE=$(shuf -e 'geography' 'subject' 'keywords' | head -n 1)
    ENTNM=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    ENTDESC=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
    curl -A "Mozilla/5.0" -L -s -d "field_input_linked_texts=$ENLT&field_input_name=$ENTNM&field_input_role=$ENROLE&field_input_description=$ENTDESC&classname=Entry" http://$host/$instance/admin/create?classname=Entry
done


M=$N #$(shuf -e '2' '3' '4' | head -n 1)
for col in `eval echo {1..$M}`;
do
    # Classe Collection, champs à remplir : title, subtitle, language, linked_director, description, publisher_note, issn
    NBLD=$(shuf -e '1' '2' '3' '4' | head -n 1)
    directors=$(printf "use $dbname\n DBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $NBLD;)
    tmp=''
    for j in $directors
    do
        if [[ ! -z $tmp ]]
        then
            tmp=$(printf "$tmp, $j")
        else
            tmp=$j
        fi
    done
    COLLD=$tmp
    COLT=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
    COLST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
    LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
    DESC=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
    PBN=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
    ISSN=$(</dev/urandom tr -dc 0-9 | head -c8;echo;)
    curl -A "Mozilla/5.0" -L -s -d "field_input_title=$COLT&field_input_subtitle=$COLST&field_input_language=$LG&field_input_linked_directors=$COLLD&field_input_description=$DESC&field_input_publisher_note=$PBN&field_input_issn=$ISSN&classname=Collection" http://$host/$instance/admin/create?classname=Collection
    collection=$(printf "use $dbname\n db.Collection.find({}, {lodel_id:1, _id:0}).sort({_id:-1}).limit(1)" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d";)
    NBNUM=$(shuf -e '30' '35' '40' | head -n 1 ) # Nombre de numéros pour cette collection

    for i in `eval echo {1..$NBNUM}`; # On remplit les numéros
    do
        NB=$(shuf -e '25' '30' '35' '40' '45' '50' '55' '60' '65' | head -n 1) # Nombre de textes pour le numéro
        NBR=$(($NB/3)) # Nombre de reviews
        NBA=$(($NBR*2)) # Nombre d'articles
        
        # Classe Issue, champs à remplir : title, subtitle, language, linked_directors, description, publisher_note, isbn, print_isbn, number, cover, print_pub_date, e_pub_date, abstract, collection, linked_parts, linked_texts
        NBLD=$(shuf -e '1' '2' '3' '4' | head -n 1)
        directors=$(printf "use $dbname\n DBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $NBLD;)
        tmp=''
        for j in $directors
        do
            if [[ ! -z $tmp ]]
            then
                tmp=$(printf "$tmp, $j")
            else
               tmp=$j
            fi
        done
        ISSLD=$tmp
        ISST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
        ISSST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
        LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
        DESC=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
        PBN=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
        ISBN=$(</dev/urandom tr -dc 0-9 | head -c10;echo;)
        PISBN=$(</dev/urandom tr -dc 0-9 | head -c10;echo;)
        ISSNU=$(lenmax=30;wcount=10; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
        ISSCOV=$(lenmax=100;wcount=15; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
        M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
        JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28'  | head -n 1)
        AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
        PPDATE=$AA'-'$M'-'$JJ
        M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
        JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28'  | head -n 1)
        AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
        EPDATE=$AA'-'$M'-'$JJ
        LNG=$(</dev/urandom tr -dc 0-9 | head -c3;echo;)
        ISSAB=$(lenmax=$LNG;wcount=200; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
        ISSLPA=''
        ISSLTXT=''
        curl -A "Mozilla/5.0" -L -s -d "field_input_title=$ISST&field_input_subtitle=$ISSST&field_input_language=$LG&field_input_linked_directors=$ISSLD&field_input_description=$DESC&field_input_publisher_note=$PBN&field_input_isbn=$ISBN&field_input_print_isbn=$PISBN&field_input_number=$ISSNU&field_input_cover=$ISSCOV&field_input_print_pub_date=$PPDATE&field_input_e_pub_date=$EPDATE&field_input_abstract=$ISSAB&field_input_collection=$collection&field_input_linked_parts=$ISSLPA&field_input_linked_texts=$ISSLTXT&classname=Issue" http://$host/$instance/admin/create?classname=Issue
        issue=$(printf "use $dbname\n db.Issue.find({}, {lodel_id:1, _id:0}).sort({_id:-1}).limit(1)" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" )
       
        # On entre les textes correspondants aux numéros indépendemment des parts
        NBT=$(shuf '2' '3' '4' '5' '6' '8' | head -n 1)
        for i in `eval echo {1..$NBT}`;
        do
            # Classe Article, champs à remplir : title, subtitle, language, text, pub_date, footnotes, linked_entries, linked_persons, linked_container, abstract, appendix, bibliography, author_note
            ATCT=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            ATCST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
            LNG=32000; #$(</dev/urandom tr -dc 0-9 | head -c5;echo;)
            ATCTXT=$(lenmax=$LNG;wcount=12000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
            JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28' | head -n 1)
            AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
            ATCDATE=$AA'-'$M'-'$JJ
            LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
            ATCFN=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            nb=$(( ( $RANDOM % 10 )  + 1 ))
            entries=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Entry.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
            tmp=""
            for i in $entries
            do
                if [[ ! -z $tmp ]]
                then
                    tmp=$(printf "$tmp, $i")
                else
                    tmp=$i
                fi
            done
            ATCLE=$tmp
            nb=$(( ( $RANDOM % 10 )  + 1 ))
            persons=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
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
            ATCLP=$tmp
            ATCLC=$issue
            LNG=$(</dev/urandom tr -dc 0-9 | head -c3;echo;)
            ATCAB=$(lenmax=$LNG;wcount=200; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
            ATCAP=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
            ATCBI=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            LNG=$(</dev/urandom tr -dc 0-9 | head -c3;echo;)
            ATCAN=$(lenmax=$LNG;wcount=200; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            curl -A "Mozilla/5.0" -L -s -d "field_input_title=$ATCT&field_input_subtitle=$ATCST&field_input_language=$LG&field_input_text=$ATCTXT&field_input_pub_date=$ATCDATE&field_input_footnotes=$ATCFN&field_input_linked_entries=$ATCLE&field_input_linked_persons=$ATCLP&field_input_linked_container=$ATCLC&field_input_abstract=$ATCAB&field_input_appendix=$ATCAP&field_input_bibliography=$ATCBI&field_input_author_note=$ATCAN&classname=Article" http://$host/$instance/admin/create?classname=Article
        done
        NBR=$(shuf '0' '2' '1' | head -n 1)
        for i in `eval echo {1..$NBR}`;
        do
        # Classe Review, champs à remplir :  title, subtitle, language, text, pub_date, footnotes, linked_entries, linked_persons, linked_container,reference
            RET=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            REST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
            LNG=32000 #$(</dev/urandom tr -dc 0-9 | head -c5;echo;)
            RETXT=$(lenmax=$LNG;wcount=12000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
            JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28' | head -n 1)
            AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
            REDATE=$AA'-'$M'-'$JJ
            LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
            REFN=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            nb=$(( ( RANDOM % 10 )  + 1 ))
            entries=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Entry.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
            tmp=""
            for i in $entries
            do
                if [[ ! -z $tmp ]]
                then
                    tmp=$(printf "$tmp, $i")
                else
                    tmp=$i
                fi
            done
            RELE=$tmp
            nb=$(( ( RANDOM % 10 )  + 1 ))
            persons=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb; )
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
            RELP=$tmp
            RELC=$issue
            REREF=$(lenmax=300;wcount=90; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
            curl -A "Mozilla/5.0" -L -s -d "field_input_title=$RET&field_input_subtitle=$REST&field_input_language=$LG&field_input_text=$RETXT&field_input_pub_date=$REDATE&field_input_footnotes=$REFN&field_input_linked_entries=$RELE&field_input_linked_persons=$RELP&field_input_linked_container=$RELC&field_input_reference=$REREF&classname=Review" http://$host/$instance/admin/create?classname=Review
        done
        NBP=$(shuf -e '2' '3'  | head -n 1) # Nombre de parts en relation directe avec des issues
        for i in `eval echo {1..$NBP}`;
        do
            # Classe Part, champs à remplir : title, subtitle, language, linked_directors, description, publisher_note, isbn, print_isbn, number, cover, print_pub_date, e_pub_date, abstract, publication
            NBLD=$(shuf -e '1' '2' '3' '4' | head -n 1)
            directors=$(printf "use $dbname\n DBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $NBLD;)
            tmp=''
            for j in $directors
            do
                if [[ ! -z $tmp ]]
                then
                    tmp=$(printf "$tmp, $j")
                else
                    tmp=$j
                fi
            done
            PALD=$tmp
            PAT=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
            PAST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
            LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
            DESC=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
            PBN=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
            issue=$(printf "use $dbname\nDBQuery.shellBatchSize = 1000\n db.Issue.find({collection:$collection}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n 1;)
            PALTXT=''
            PALP=''
            curl -A "Mozilla/5.0" -L -s -d "field_input_title=$PAT&field_input_subtitle=$PAST&field_input_language=$LG&field_input_linked_directors=$PALD&field_input_description=$DESC&field_input_publisher_note=$PBN&field_input_publication=$issue&field_input_linked_parts=$PALP&field_input_linked_texts=$PALTXT&classname=Part" http://$host/$instance/admin/create?classname=Part
            part=$(printf "use $dbname\n db.Part.find({}, {lodel_id:1, _id:0}).sort({_id:-1}).limit(1)" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" )
       
            # On entre les textes correspondants aux  parts
            NBPANBT=$(shuf '2' '3' '4' | head -n 1)
            for i in `eval echo {1..$NBPANBT}`;
            do
                # Classe Article, champs à remplir : title, subtitle, language, text, pub_date, footnotes, linked_entries, linked_persons, linked_container, abstract, appendix, bibliography, author_note
                ATCT=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                ATCST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
                LNG=32000 #$(</dev/urandom tr -dc 0-9 | head -c5;echo;)
                ATCTXT=$(lenmax=$LNG;wcount=12000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
                JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28' | head -n 1)
                AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
                ATCDATE=$AA'-'$M'-'$JJ
                LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                ATCFN=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                nb=$(( ( RANDOM % 10 )  + 1 ))
                entries=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Entry.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
                tmp=""
                for i in $entries
                do
                    if [[ ! -z $tmp ]]
                    then
                        tmp=$(printf "$tmp, $i")
                    else
                        tmp=$i
                    fi
                done
                ATCLE=$tmp
                nb=$(( ( RANDOM % 10 )  + 1 ))
                persons=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
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
                ATCLP=$tmp
                ATCLC=$part
                LNG=$(</dev/urandom tr -dc 0-9 | head -c3;echo;)
                ATCAB=$(lenmax=$LNG;wcount=200; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                ATCAP=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                ATCBI=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                LNG=$(</dev/urandom tr -dc 0-9 | head -c3;echo;)
                ATCAN=$(lenmax=$LNG;wcount=200; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                curl -A "Mozilla/5.0" -L -s -d "field_input_title=$ATCT&field_input_subtitle=$ATCST&field_input_language=$LG&field_input_text=$ATCTXT&field_input_pub_date=$ATCDATE&field_input_footnotes=$ATCFN&field_input_linked_entries=$ATCLE&field_input_linked_persons=$ATCLP&field_input_linked_container=$ATCLC&field_input_abstract=$ATCAB&field_input_appendix=$ATCAP&field_input_bibliography=$ATCBI&field_input_author_note=$ATCAN&classname=Article" http://$host/$instance/admin/create?classname=Article
            done
            NBPANBR=$(shuf '0' '1' '2' | head -n 1)
            for i in `eval echo {1..$NBPANBR}`;
            do
            # Classe Review, champs à remplir :  title, subtitle, language, text, pub_date, footnotes, linked_entries, linked_persons, linked_container,reference
                RET=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                REST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
                LNG=32000 #$(</dev/urandom tr -dc 0-9 | head -c5;echo;)
                RETXT=$(lenmax=$LNG;wcount=12000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
                JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28' | head -n 1)
                AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
                REDATE=$AA'-'$M'-'$JJ
                LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                REFN=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                nb=$(( ( RANDOM % 10 )  + 1 ))
                entries=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Entry.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
                tmp=""
                for i in $entries
                do
                    if [[ ! -z $tmp ]]
                    then
                        tmp=$(printf "$tmp, $i")
                    else
                        tmp=$i
                    fi
                done
                RELE=$tmp
                nb=$(( ( RANDOM % 10 )  + 1 ))
                persons=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb; )
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
                RELP=$tmp
                RELC=$part
                REREF=$(lenmax=300;wcount=90; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                curl -A "Mozilla/5.0" -L -s -d "field_input_title=$RET&field_input_subtitle=$REST&field_input_language=$LG&field_input_text=$RETXT&field_input_pub_date=$REDATE&field_input_footnotes=$REFN&field_input_linked_entries=$RELE&field_input_linked_persons=$RELP&field_input_linked_container=$RELC&field_input_reference=$REREF&classname=Review" http://$host/$instance/admin/create?classname=Review
            done
            NBSP=$(shuf -e '0' '1' '2' '3'  | head -n 1) # Nombre de parts en relation avec d'autres parts
            for i in `eval echo {1..$NBSP}`;
            do
                # Classe Part, champs à remplir : title, subtitle, language, linked_director, description, publisher_note, isbn, print_isbn, number, cover, print_pub_date, e_pub_date, abstract, publication
                NBLD=$(shuf -e '1' '2' '3' '4' | head -n 1)
                directors=$(printf "use $dbname\n DBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $NBLD;)
                tmp=''
                for j in $directors
                do
                   if [[ ! -z $tmp ]]
                   then
                            tmp=$(printf "$tmp, $j")
                        else
                            tmp=$i
                        fi
                done
                PALD=$tmp
                PAT=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
                PAST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
                LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
                DESC=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
                PBN=$(lenmax=500;wcount=100; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/") 
                issue=$(printf "use $dbname\nDBQuery.shellBatchSize = 1000\n db.Issue.find({collection:$collection}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n 1;)
                part=$(printf "use $dbname\nDBQuery.shellBatchSize = 1000\n db.Part.find({publication: $issue}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n 1;)
                PALTXT=''
                PALP=''
                curl -A "Mozilla/5.0" -L -s -d "field_input_title=$PAT&field_input_subtitle=$PAST&field_input_language=$LG&field_input_linked_directors=$PALD&field_input_description=$DESC&field_input_publisher_note=$PBN&field_input_publication=$part&field_input_linked_parts=$PALP&field_input_linked_texts=$PALTXT&classname=Part" http://$host/$instance/admin/create?classname=Part
                part=$(printf "use $dbname\n db.Part.find({}, {lodel_id:1, _id:0}).sort({_id:-1}).limit(1)" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd | sed "1,3d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" )
       
                # On entre les textes correspondants aux numéros indépendemment des parts
                for i in `eval echo {1..$NBA}`;
                do
                    # Classe Article, champs à remplir : title, subtitle, language, text, pub_date, footnotes, linked_entries, linked_persons, linked_container, abstract, appendix, bibliography, author_note
                    ATCT=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    ATCST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
                    LNG=32000 #$(</dev/urandom tr -dc 0-9 | head -c5;echo;)
                    ATCTXT=$(lenmax=$LNG;wcount=12000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
                    JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28' | head -n 1)
                    AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
                    ATCDATE=$AA'-'$M'-'$JJ
                    LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                    ATCFN=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    nb=$(( ( RANDOM % 10 )  + 1 ))
                    entries=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Entry.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
                    tmp=""
                    for i in $entries
                    do
                        if [[ ! -z $tmp ]]
                        then
                            tmp=$(printf "$tmp, $i")
                        else
                            tmp=$i
                        fi
                    done
                    ATCLE=$tmp
                    nb=$(( ( RANDOM % 10 )  + 1 ))
                    persons=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
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
                    ATCLP=$tmp
                    ATCLC=$part
                    LNG=$(</dev/urandom tr -dc 0-9 | head -c3;echo;)
                    ATCAB=$(lenmax=$LNG;wcount=200; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                    ATCAP=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                    ATCBI=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    LNG=$(</dev/urandom tr -dc 0-9 | head -c3;echo;)
                    ATCAN=$(lenmax=$LNG;wcount=200; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    curl -A "Mozilla/5.0" -L -s -d "field_input_title=$ATCT&field_input_subtitle=$ATCST&field_input_language=$LG&field_input_text=$ATCTXT&field_input_pub_date=$ATCDATE&field_input_footnotes=$ATCFN&field_input_linked_entries=$ATCLE&field_input_linked_persons=$ATCLP&field_input_linked_container=$ATCLC&field_input_abstract=$ATCAB&field_input_appendix=$ATCAP&field_input_bibliography=$ATCBI&field_input_author_note=$ATCAN&classname=Article" http://$host/$instance/admin/create?classname=Article
                done
                for i in `eval echo {1..$NBR}`;
                do
                # Classe Review, champs à remplir :  title, subtitle, language, text, pub_date, footnotes, linked_entries, linked_persons, linked_container,reference
                    RET=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    REST=$(lenmax=100;wcount=20; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    LG=$(shuf -e 'fr' 'en' 'es' 'ger' 'it'| head -n 1)
                    LNG=32000 #$(</dev/urandom tr -dc 0-9 | head -c5;echo;)
                    RETXT=$(lenmax=$LNG;wcount=12000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    M=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' | head -n 1)
                    JJ=$(shuf -e '01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23' '24' '25' '26' '27' '28' | head -n 1)
                    AA=$(shuf -e '2012' '2005' '2010' '2015' '2016'| head -n 1)
                    REDATE=$AA'-'$M'-'$JJ
                    LNG=$(</dev/urandom tr -dc 0-9 | head -c4;echo;)
                    REFN=$(lenmax=$LNG;wcount=2000; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    nb=$(( ( RANDOM % 10 )  + 1 ))
                    entries=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Entry.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb;)
                    tmp=""
                    for i in $entries
                    do
                        if [[ ! -z $tmp ]]
                        then
                            tmp=$(printf "$tmp, $i")
                        else
                            tmp=$i
                        fi
                    done
                    RELE=$tmp
                    nb=$(( ( RANDOM % 10 )  + 1 ))
                    persons=$(printf "use $dbname\nDBQuery.shellBatchSize = 30000\n db.Person.find({}, {lodel_id:1, _id:0})" | mongo  $HOSTDB/admin -u $dbuser -p $dbpwd  | sed "1,4d" | sed -e "s/{ \"lodel_id\" : //g" | sed -e "s/ }//g" | sed "\$d" | shuf | head -n $nb; )
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
                    RELP=$tmp
                    RELC=$issue
                    REREF=$(lenmax=300;wcount=90; rlenmax=$(expr $lenmax - 1); echo $(shuf /usr/share/dict/words | head -n $wcount | tr -s "\n" " ") | sed -E "s/^(.{$rlenmax}).*$/\1/")
                    curl -A "Mozilla/5.0" -L -s -d "field_input_title=$RET&field_input_subtitle=$REST&field_input_language=$LG&field_input_text=$RETXT&field_input_pub_date=$REDATE&field_input_footnotes=$REFN&field_input_linked_entries=$RELE&field_input_linked_persons=$RELP&field_input_linked_container=$RELC&field_input_reference=$REREF&classname=Review" http://$host/$instance/admin/create?classname=Review
                done
            done
        done
    done
done