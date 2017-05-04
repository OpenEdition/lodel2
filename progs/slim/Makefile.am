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


bin_SCRIPTS = slim
CLEANFILES = $(bin_SCRIPTS) slim_instances.json slim_instances_pid.json
EXTRA_DIST = slim.py install_model emfile.pickle

lodel2_scripts_dir = $(datadir)/lodel2/scripts

lodel2datadir = $(datadir)/lodel2

slimdatadir = $(lodel2datadir)/slim
slimdata_DATA = emfile.pickle

install_model_dir = $(lodel2datadir)/install_model
install_model__DATA = 	install_model/loader.py \
			install_model/lodel_admin.py \
			install_model/Makefile 

slim_conf_model_dir = $(install_model_dir)/conf.d/
slim_conf_model__DATA = install_model/conf.d/lodel2.ini

slim_var__DATA = slim_instances.json slim_instances_pid.json
slim_var_dir = $(localstatedir)/lodel2/slim/

slim_instances.json:
	touch slim_instances.json
slim_instances_pid.json:
	touch slim_instances_pid.json

do_subst = sed -e 's,\[@\]LODEL2_PROGSDIR\[@\],$(lodel2_scripts_dir),g' \
	-e 's,\[@\]SLIM_DATADIR\[@\],$(slimdatadir),g' \
	-e 's,\[@\]INSTALLMODEL_DIR\[@\],$(install_model_dir),g' \
	-e 's,\[@\]SLIM_VAR_DIR\[@\],$(slim_var_dir),g' \
	-e 's,\[@\]PKGPYTHONDIR\[@\],$(pkgpythondir),g'

slim: slim.py
	$(do_subst) < $(srcdir)/slim.py > slim
	chmod +x slim

install-data-hook:
	chmod +x ${DESTDIR}$(install_model_dir)/lodel_admin.py

