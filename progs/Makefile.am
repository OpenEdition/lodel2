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


SUBDIRS=slim

lodel2_scripts_dir = $(datadir)/lodel2/scripts
lodel2_scripts__DATA = create_instance mass_deploy
CLEANFILES = create_instance mass_deploy mass_deploy.cfg
EXTRA_DIST = create_instance.sh mass_deploy.sh

lodel2conf_DATA = mass_deploy.cfg
lodel2confdir=$(sysconfdir)/lodel2


do_subst = sed 	-e 's,\[@\]PKGPYTHONDIR\[@\],$(pkgpythondir),g' \
		-e 's,\[@\]LODEL2_PROGSDIR\[@\],$(lodel2_scripts_dir),g' \
		-e 's,\[@\]LODEL2_CONFDIR\[@\],$(lodel2confdir),g'

#There is clearly a way to factorise those rules
mass_deploy: mass_deploy.sh
	$(do_subst) < $(srcdir)/mass_deploy.sh > mass_deploy
	chmod +x mass_deploy

mass_deploy.cfg:
	echo -e "#Uncomment following lines replacing values by your own\n#MONGODB_ADMIN_USER='admin'\n#MONGODB_ADMIN_PASSWORD='pass'\n#Following configurations are optional\nMONGODB_DB_PREFIX='lodel2'\n#You can give only an host or a HOSTNAME:PORT\n#WARNING !!! : mass_deploy script does not forward MONGODB_HOST in instances\n#configurations\n#MONGODB_HOST=''" > mass_deploy.cfg

create_instance: create_instance.sh
	$(do_subst) < $(srcdir)/create_instance.sh > create_instance
	chmod +x create_instance

install-data-hook:
	chmod +x ${DESTDIR}$(datadir)/lodel2/scripts/*

