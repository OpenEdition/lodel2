SUBDIRS=slim

lodel2_scripts_dir = $(datadir)/lodel2/scripts
lodel2_scripts__DATA = create_instance
CLEANFILES = $(lodel2_scripts__DATA)

do_subst = sed -e 's,\[@\]PKGPYTHONDIR\[@\],$(pkgpythondir),g' 

create_instance: create_instance.sh
	$(do_subst) < $(srcdir)/create_instance.sh > create_instance
	chmod +x create_instance

install-data-hook:
	chmod +x $(datadir)/lodel2/scripts/create_instance
