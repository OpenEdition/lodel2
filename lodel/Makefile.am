SUBDIRS=auth editorial_model leapi plugin settings utils

lodel_PYTHON = *.py
CLEANFILES = buildconf.py


all-local: buildconf.py

lodeldir=$(pkgpythondir)/

distclean-local:
	-rm Makefile Makefile.in

do_subst = sed -e 's,\[@\]LODEL2_VARDIR\[@\],$(localstatedir)/lodel2/,g'

buildconf.py: buildconf.py.am
	$(do_subst) < $(srcdir)/buildconf.py.am > buildconf.py

