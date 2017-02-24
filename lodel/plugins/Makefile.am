plugins_PYTHON=__init__.py

pluginsdir=$(pkgpythondir)/plugins
lodel2confdir=$(sysconfdir)/lodel2

install-data-hook:
	$(MKDIR_P) $(pluginsdir); cp -R * $(pluginsdir) && rm $(pluginsdir)/Makefile* ;\
	$(MKDIR_P) $(lodel2confdir); \
	$(LN_S) $(pluginsdir) $(lodel2confdir)/plugins

uninstall-hook:
	-rm -R ${DESTDIR}$(pluginsdir)
	-rm -R $(lodel2confdir)
