plugins_PYTHON=__init__.py

pluginsdir=$(pkgpythondir)/plugins
lodel2confdir=$(sysconfdir)/lodel2

install-data-hook:
	mkdir -p ${DESTDIR}$(pluginsdir); cp -R * ${DESTDIR}$(pluginsdir) && rm ${DESTDIR}$(pluginsdir)/Makefile* ;\
	mkdir -p ${DESTDIR}$(lodel2confdir); \
	if [ ! -d ${DESTDIR}$(lodel2confdir)/plugins ]; \
    then \
        ln -rs -t ${DESTDIR}$(lodel2confdir) $(pluginsdir); \
    fi


uninstall-hook:
	-rm -R ${DESTDIR}$(pluginsdir)
	-rm -R $(lodel2confdir)
