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


SUBDIRS = lodel progs lodelsites
EXTRA_DIST = runtest examples tests debian
CLEANFILES = runtest

lodel2_localstate_DATA =
lodel2_localstatedir=$(localstatedir)/lodel2

lodel2datadir=$(datadir)/lodel2
install_model_dir = $(lodel2datadir)/install_model

#python=/usr/bin/env python3
python=@PYTHON@
dyncode_filename='lodel/leapi/dyncode.py'

docdir=${datarootdir}/doc/lodel2

# Doxygen doc generation targets
doxygen:
	test -z "@DOCOK@" && echo -e "\n\nUnable to generate documentation. See ./configure output for details\n\n" >&2 || make generate-doc

generate-doc: clean doc_graphviz
	doxygen

doc_graphviz:
	cd doc/img/graphviz; make


do_subst = sed -e 's,\[@\]INSTALLMODEL_DIR\[@\],$(install_model_dir),g' 

runtest: ./runtest.sh
	$(do_subst) < $(srcdir)/runtest.sh > runtest
	chmod +x runtest

#Adding logdir creation on install
install-data-hook:
	mkdir -p ${DESTDIR}$(lodel2_localstatedir); mkdir -p ${DESTDIR}$(docdir); cp README ${DESTDIR}$(docdir);

#Making debian package
deb: dist
	mkdir debian_package;\
	tar -xvf ${PACKAGE}-${VERSION}.tar.gz -C ./debian_package;\
	cd debian_package/${PACKAGE}-${VERSION};\
	dpkg-buildpackage -rfakeroot;

# Test em update ( examples/em_test.pickle )
em_test: em_test.py
	$(python) em_test.py

# Test em update ( examples/em_test.pickle )
em_simple: editorial_models/em_simple.py
	$(python) editorial_models/em_simple.py
	
# generate leapi dynamic code
dyncode: examples/em_test.pickle
	$(python) scripts/refreshdyn.py examples/em_test.pickle $(dyncode_filename) && echo -e "\n\nCode generated in $(dyncode_filename)"

# generate leapi dynamic code
dyncode_simple: examples/em_simple.pickle
	$(python) scripts/refreshdyn.py examples/em_simple.pickle $(dyncode_filename) && echo -e "\n\nCode generated in $(dyncode_filename)"

# run tests
checks: runtest
	./runtest -v

unittest: checks

#Cleaning documentation and dyncode
clean-local: cleandoc
	-rm -vR doc/html doc/doxygen_sqlite3.db
cleandoc:
	-rm -v $(dyncode_filename)

#other cleans
distclean-local:
	-rm -vR debian_package ${PACKAGE}-${VERSION}.tar.gz
	-find . -name Makefile.in -delete

gitclean: distclean cleandoc
	-rm -vR autom4te.cache/ aclocal.m4 install-sh missing py-compile configure; find ./ -name Makefile.in |xargs rm -v

.PHONY: cleandoc tests doc
