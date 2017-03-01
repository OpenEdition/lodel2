bin_SCRIPTS = slim
CLEANFILES = $(bin_SCRIPTS) slim_instances.json slim_instances_pid.json
EXTRA_DIST = slim.py install_model multisite_install_model emfile.pickle

lodel2_scripts_dir = $(datadir)/lodel2/scripts

lodel2datadir = $(datadir)/lodel2

slimdatadir = $(lodel2datadir)/slim
slimdata_DATA = emfile.pickle

install_model_dir = $(lodel2datadir)/install_model
install_model__DATA = 	install_model/loader.py \
			install_model/lodel_admin.py \
			install_model/Makefile 

multisite_install_model_dir = $(lodel2datadir)/multisite_install_model
multisite_install_model__DATA = multisite_install_model/lodel_admin.py \
			multisite_install_model/Makefile 

#Forgotten files in git commits ??
multisite_install_model:
	$(MKDIR_P) multisite_install_model
multisite_install_model/lodel_admin.py: multisite_install_model install_model/lodel_admin.py
	cp install_model/lodel_admin.py multisite_install_model/lodel_admin.py
multisite_install_model/Makefile: multisite_install_model install_model/Makefile
	cp install_model/Makefile multisite_install_model/Makefile
	


slim_conf_model_dir = $(install_model_dir)/conf.d/
slim_conf_model__DATA = install_model/conf.d/lodel2.ini

slim_var__DATA = slim_instances.json slim_instances_pid.json
slim_var_dir = $(localstatedir)/lodel2/slim/

slim_instances.json:
	touch slim_instances.json
slim_instances_pid.json:
	touch slim_instances_pid.json

do_subst = sed -e 's,\[@\]LODEL2_PROGSDIR\[@\],$(lodel2_scripts_dir),g' \
	-e 's,\[@\]SLIM_DATADIR\[@\],$(slimdatadir),g' \
	-e 's,\[@\]INSTALLMODEL_DIR\[@\],$(install_model_dir),g' \
	-e 's,\[@\]MULTISITE_INSTALLMODEL_DIR\[@\],$(multisite_install_model_dir),g' \
	-e 's,\[@\]SLIM_VAR_DIR\[@\],$(slim_var_dir),g' \
	-e 's,\[@\]PKGPYTHONDIR\[@\],$(pkgpythondir),g'

slim: slim.py
	$(do_subst) < $(srcdir)/slim.py > slim
	chmod +x slim

install-data-hook:
	chmod +x ${DESTDIR}$(install_model_dir)/lodel_admin.py
	chmod +x ${DESTDIR}$(multisite_install_model_dir)/lodel_admin.py

