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


import os
import sys
import shlex
import warnings

#Here we have to bootstrap a minimal __loader__ context in order
#to be able to load the settings
#
#This file (once bootstraped) start a new process for uWSGI. uWSGI then
#run lodel.plugins.multisite.run.application function
try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext

from lodel import buildconf

LodelContext.init(LodelContext.MULTISITE)
LodelContext.set(None) #Loading context creation
#Multisite instance settings loading
CONFDIR = os.path.join(os.getcwd(), 'conf.d')
if not os.path.isdir(CONFDIR):
    warnings.warn('%s do not exists, default settings used' % CONFDIR)
LodelContext.expose_modules(globals(), {
    'lodel.settings.settings': [('Settings', 'settings')],
    'lodel.plugins.multisite.confspecs': 'multisite_confspecs'})
if not settings.started():
    settings('./conf.d', multisite_confspecs.LODEL2_CONFSPECS)

LodelContext.expose_modules(globals(), {
    'lodel.settings': ['Settings']})

##@brief Starts uwsgi in background using settings
def uwsgi_fork():
    
    sockfile = os.path.join(buildconf.LODEL2VARDIR, 'uwsgi_sockets/')
    if not os.path.isdir(sockfile):
        os.mkdir(sockfile)
    sockfile = os.path.join(sockfile, 'uwsgi_lodel2_multisite.sock')
    logfile = os.path.join(
        buildconf.LODEL2LOGDIR, 'uwsgi_lodel2_multisite.log')
        
    cmd='{uwsgi} --plugin python3 --http-socket {addr}:{port} --module \
lodel.plugins.multisite.run --socket {sockfile} --logto {logfile} -p {uwsgiworkers}'
    cmd = cmd.format(
                addr = Settings.server.listen_address,
                port = Settings.server.listen_port,
                uwsgi= Settings.server.uwsgicmd,
                sockfile=sockfile,
                logfile = logfile,
                uwsgiworkers = Settings.server.uwsgi_workers)
    if Settings.server.virtualenv is not None:
        cmd += " --virtualenv %s" % Settings.webui.virtualenv

    try:
        args = shlex.split(cmd)
        print("Running %s" % cmd)
        exit(os.execl(args[0], *args))
    except Exception as e:
        print("Webui plugin uwsgi execl fails cmd was '%s' error : " % cmd,
            e, file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    uwsgi_fork()
        
