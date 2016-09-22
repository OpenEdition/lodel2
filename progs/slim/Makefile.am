bin_SCRIPTS = slim
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = slim.py install_model emfile.pickle

lodel2_scripts_dir = $(datadir)/lodel2/scripts

slimdatadir = $(datadir)/lodel2/slim/
slimdata_DATA = emfile.pickle

slim_install_model_dir = $(slimdatadir)/install_model
slim_install_model__DATA = 	install_model/loader.py \
				install_model/lodel_admin.py \
				install_model/Makefile 

slim_conf_model_dir = $(slim_install_model_dir)/conf.d/
slim_conf_model__DATA = install_model/conf.d/lodel2.ini

slim_var__DATA = slim_instances.json slim_instances_pid.json
slim_var_dir = $(localstatedir)/lodel2/slim/

slim_instances.json:
	touch slim_instances.json
slim_instances_pid.json:
	touch slim_instances_pid.json

do_subst = sed -e 's,\[@\]LODEL2_PROGSDIR\[@\],$(lodel2_scripts_dir),g' \
	-e 's,\[@\]SLIM_DATADIR\[@\],$(slimdatadir),g' \
	-e 's,\[@\]SLIM_INSTALLMODEL_DIR\[@\],$(slim_install_model_dir),g' \
	-e 's,\[@\]SLIM_VAR_DIR\[@\],$(slim_var_dir),g' \
	-e 's,\[@\]PKGPYTHONDIR\[@\],$(pkgpythondir),g'

slim: slim.py
	$(do_subst) < $(srcdir)/slim.py > slim
	chmod +x slim

