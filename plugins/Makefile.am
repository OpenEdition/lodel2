plugins_PYTHON=__init__.py

pluginsdir=$(pkgpythondir)/plugins

install-data-local:
	mkdir ${DESTDIR}$(pluginsdir); cp -R * ${DESTDIR}$(pluginsdir) && rm ${DESTDIR}$(pluginsdir)/Makefile*

uninstall-hook:
	-rm -R ${DESTDIR}$(pluginsdir)
