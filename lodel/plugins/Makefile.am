plugins_PYTHON=__init__.py

pluginsdir=$(pkgpythondir)/plugins
lodel2confdir=$(sysconfdir)/lodel2

install-data-hook:
	-@$(MKDIR_P) ${DESTDIR}$(lodel2confdir)
	$(MKDIR_P) ${DESTDIR}$(pluginsdir); cp -R * ${DESTDIR}$(pluginsdir) && rm -v ${DESTDIR}$(pluginsdir)/Makefile* ;
	cd ${DESTDIR};
	$(MKDIR_P) ./$(lodel2confdir);
	$(LN_S) -rt ${DESTDIR}$(lodel2confdir) .$(pluginsdir)

uninstall-hook:
	-rm -R ${DESTDIR}$(pluginsdir)
	-rm -R $(lodel2confdir)
