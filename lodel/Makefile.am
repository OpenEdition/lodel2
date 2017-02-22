SUBDIRS=auth editorial_model leapi plugin settings utils plugins validator mlnamedobject
EXTRA_DIST = plugins
lodel_PYTHON = *.py
CLEANFILES = buildconf.py


all-local: buildconf.py

lodeldir=$(pkgpythondir)/

gitclean:
	-rm Makefile Makefile.in

logdir = $(localstatedir)/log/lodel2/

do_subst = sed 	-e 's,\[@\]LODEL2_VARDIR\[@\],$(localstatedir)/lodel2/,g' \
		-e 's,\[@\]LODEL2_LOGDIR\[@\],$(logdir),g'


install-data-hook:
	-mkdir -p ${DESTDIR}$(logdir)

uninstall-hook:
	-rmdir ${DESTDIR}$(logdir)

buildconf.py: buildconf.py.am
	$(do_subst) < $(srcdir)/buildconf.py.am > buildconf.py

