#!/bin/bash
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


schroot_cmd="schroot --directory /tmp -c lodel2"
chrootdir="/localdata/lodel2-chroot"
chroot_tarball="/localdata/lodel2-chroot.raz.tar.gz"
chroot_instance_dir="/tmp/lodel2_instances/"

mongodb_host="147.94.102.23"
mongodb_login="admin"
mongodb_pass="pass"



echo "##############"
echo "# Chroot RAZ #"
echo "##############"
mv $chrootdir ${chrootdir}_bck
tar -xf $chroot_tarball && rm -R ${chrootdir}_bck || echo "RAZ failed, backup can be found in lodel2-chroot_bck"

echo "Installing lodel2 in chroot"
cp -v /tmp/lodel2_0.1_amd64.deb $chrootdir/tmp/
$schroot_cmd  -- /bin/bash -c 'dpkg -i /tmp/lodel2_0.1_amd64.deb ; apt install -yf'
echo "####################"
echo "# Lodel2 installed #"
echo "####################"
echo ""
echo "#########################"
echo "# Installing other deps #"
echo "#########################"
$schroot_cmd -- apt -y install mongodb-clients pwgen wamerican vim

echo "##########################################"
echo "# Configuring mass_deploy mongodb access #"
echo "##########################################"
$schroot_cmd -- bash -c "echo -e \"MONGODB_ADMIN_USER='$mongodb_login'\nMONGODB_ADMIN_PASSWORD='$mongodb_pass'\nMONGODB_HOST='$mongodb_host'\" >> /etc/lodel2/mass_deploy.cfg"
$schroot_cmd -- bash -c "echo exit | mongo $mongodb_host --quiet -u $mongodb_login -p $mongodb_pass --authenticationDatabase admin && echo Connection to mongodb ok || echo connection fails"

echo "####################################"
echo "# Preparing lodel2 standalone mode #"
echo "####################################"

$schroot_cmd -- mkdir -vp $chroot_instance_dir
$schroot_cmd -- cp -v /usr/lib/python3/dist-packages/lodel/plugins/multisite/loader.py $chroot_instance_dir

echo -e "\n\nChroot RAZ and ready to run lodel2"
#echo -e "\tYou are in chroot now\n\n"
#$schroot_cmd

