SUBDIRS=auth editorial_model leapi plugin settings utils

lodel_PYTHON = *.py
CLEANFILES = buildconf.py


all-local: buildconf.py

lodeldir=$(pkgpythondir)/

distclean-local:
	-rm Makefile Makefile.in

logdir = $(localstatedir)/log/lodel2/

do_subst = sed 	-e 's,\[@\]LODEL2_VARDIR\[@\],$(localstatedir)/lodel2/,g' \
		-e 's,\[@\]LODEL2_LOGDIR\[@\],$(logdir),g'


install-data-hook:
	-mkdir -p $(logdir)

uninstall-hook:
	-rmdir $(logdir)

buildconf.py: buildconf.py.am
	$(do_subst) < $(srcdir)/buildconf.py.am > buildconf.py

