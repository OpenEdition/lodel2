plugins_PYTHON=__init__.py

pluginsdir=$(pkgpythondir)/plugins

install-data-local:
	mkdir $(pluginsdir); cp -R * $(pluginsdir) && rm $(pluginsdir)/Makefile*

distclean-local:
	-rm -R Makefile Makefile.in $(pluginsdir)
