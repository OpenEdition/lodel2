plugins_PYTHON=__init__.py

pluginsdir=$(pkgpythondir)/plugins
lodel2confdir=$(sysconfdir)/lodel2

install-data-hook:
	mkdir ${DESTDIR}$(pluginsdir); cp -R * ${DESTDIR}$(pluginsdir) && rm ${DESTDIR}$(pluginsdir)/Makefile* ;\
	cd ${DESTDIR}; \
	mkdir -p ./$(lodel2confdir); \
	ln -rs -t ${DESTDIR}$(lodel2confdir) .$(pluginsdir)

uninstall-hook:
	-rm -R ${DESTDIR}$(pluginsdir)
	-rm -R $(lodel2confdir)
