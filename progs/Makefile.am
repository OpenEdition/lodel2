include $(top_builddir)/Makefile-common.am.inc

SUBDIRS=slim

lodel2_scripts_dir = $(datadir)/lodel2/scripts
lodel2_scripts__DATA = create_instance create_multisite mass_deploy
CLEANFILES = create_instance create_multisite mass_deploy mass_deploy.cfg
EXTRA_DIST = create_instance.sh create_multisite.sh mass_deploy.sh

lodel2conf_DATA = mass_deploy.cfg
lodel2confdir=$(sysconfdir)/lodel2
lodel2statedir=$(localstatedir)/lodel2
lodel2datadir = $(datadir)/lodel2
install_model_dir = $(lodel2datadir)/install_model
multisite_install_model_dir = $(lodel2datadir)/multisite_install_model

do_subst = sed -e 's,\[@\]PKGPYTHONDIR\[@\],$(pkgpythondir),g' \
		-e 's,\[@\]LODEL2_DATADIR\[@\],$(lodel2datadir),g' \
		-e 's,\[@\]LODEL2_PROGSDIR\[@\],$(lodel2_scripts_dir),g' \
		-e 's,\[@\]LODEL2_CONFDIR\[@\],$(lodel2confdir),g' \
		-e 's,\[@\]LODEL2_VARDIR\[@\],$(lodel2statedir),g' \
		-e 's,\[@\]INSTALLMODEL_DIR\[@\],$(install_model_dir),g' \
		-e 's,\[@\]MULTISITE_INSTALLMODEL_DIR\[@\],$(multisite_install_model_dir),g' \
		-e 's,\[@\]LODELSITES_DATA_DIRNAME\[@\],$(lodel2_multisite_data_dirname),g' \
		-e 's,\[@\]LODELSITES_CTX_DIRNAME\[@\],$(lodel2_multisite_ctx_dirname),g'

#There is clearly a way to factorise those rules
mass_deploy: mass_deploy.sh
	$(do_subst) < $(srcdir)/mass_deploy.sh > mass_deploy
	chmod +x mass_deploy

mass_deploy.cfg:
	echo -e "#Uncomment following lines replacing values by your own\n#MONGODB_ADMIN_USER='admin'\n#MONGODB_ADMIN_PASSWORD='pass'\n#Following configurations are optional\nMONGODB_DB_PREFIX='lodel2'\n#You can give only an host or a HOSTNAME:PORT\n#WARNING !!! : mass_deploy script does not forward MONGODB_HOST in instances\n#configurations\n#MONGODB_HOST=''" > mass_deploy.cfg

create_instance: create_instance.sh
	$(do_subst) < $(srcdir)/create_instance.sh > create_instance
	chmod +x create_instance

create_multisite: create_multisite.sh
	$(do_subst) < $(srcdir)/create_multisite.sh > create_multisite
	chmod +x create_multisite

install-data-hook:
	chmod +x ${DESTDIR}$(datadir)/lodel2/scripts/*
	
