SUBDIRS=slim

lodel2_scripts_dir = $(datadir)/lodel2/scripts
lodel2_scripts__DATA = create_instance mass_deploy create_mongodb.sh
CLEANFILES = create_instance mass_deploy mass_deploy.cfg

lodel2conf_DATA = mass_deploy.cfg
lodel2confdir=$(sysconfdir)/lodel2


do_subst = sed 	-e 's,\[@\]PKGPYTHONDIR\[@\],$(pkgpythondir),g' \
		-e 's,\[@\]LODEL2_PROGSDIR\[@\],$(lodel2_scripts_dir),g' \
		-e 's,\[@\]LODEL2_CONFDIR\[@\],$(lodel2confdir),g'

#There is clearly a way to factorise those rules
mass_deploy: mass_deploy.sh
	$(do_subst) < $(srcdir)/mass_deploy.sh > mass_deploy
	chmod +x mass_deploy

create_mongodb.sh: ;
mass_deploy.cfg:
	echo -e "#Uncomment following lines replacing values by your own\n#MONGODB_ADMIN_USER='admin'\n#MONGODB_ADMIN_PASSWORD='pass'\n#Following configurations are optional\nMONGODB_DB_PREFIX='lodel2'\n#You can give only an host or a HOSTNAME:PORT\n#WARNING !!! : mass_deploy script does not forward MONGODB_HOST in instances\n#configurations\n#MONGODB_HOST=''" > mass_deploy.cfg

create_instance: create_instance.sh
	$(do_subst) < $(srcdir)/create_instance.sh > create_instance
	chmod +x create_instance

install-data-hook:
	chmod +x $(datadir)/lodel2/scripts/*
