# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


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

