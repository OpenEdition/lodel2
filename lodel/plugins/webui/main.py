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


import os, os.path
import sys
import shlex

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin': ['LodelHook'],
    'lodel.settings': ['Settings']})

from lodel import buildconf #<-- This one is common to the build

PLUGIN_PATH = os.path.dirname(__file__)

##@brief Return the root url of the instance
#@warning no trailing slash
def root_url():
    return Settings.sitename

def static_url():
    return Settings.webui.static_url

##@brief uwsgi startup demo
@LodelHook('lodel2_loader_main')
def uwsgi_fork(hook_name, caller, payload):
    
    standalone = Settings.webui.standalone
    if standalone.lower() == 'false':
        return
    else:
        sockfile = os.path.join(buildconf.LODEL2VARDIR, 'uwsgi_sockets/')
        if not os.path.isdir(sockfile):
            os.mkdir(sockfile)
        sockfile = os.path.join(sockfile,
            Settings.sitename.replace('/','_') + '.sock')
        logfile = os.path.join(
            buildconf.LODEL2LOGDIR, 'uwsgi_%s.log' % (
                Settings.sitename.replace('/', '_')))
            
        if standalone.lower() == 'true':
            cmd='{uwsgi} --plugin python3 --http-socket {addr}:{port} --module \
plugins.webui.run --socket {sockfile} --logto {logfile} -p {uwsgiworkers}'
            cmd = cmd.format(
                        addr = Settings.webui.listen_address,
                        port = Settings.webui.listen_port,
                        uwsgi= Settings.webui.uwsgicmd,
                        sockfile=sockfile,
                        logfile = logfile,
                        uwsgiworkers = Settings.webui.uwsgi_workers)
            if Settings.webui.virtualenv is not None:
                cmd += " --virtualenv %s" % Settings.webui.virtualenv

        elif Settings.webui.standalone == 'uwsgi':
            cmd = '{uwsgi} --plugin python3 --ini ./plugins/webui/uwsgi/uwsgi.ini \
--socket {sockfile} --logto {logfile} -p {uwsgiworkers}'
            cmd = cmd.format(uwsgi = Settings.webui.uwsgicmd, 
                sockfile = sockfile, logfile = logfile, uwsgiworkers=Settings.webui.uwsgi_workers)
        
        try:
            args = shlex.split(cmd)
            exit(os.execl(args[0], *args))
        except Exception as e:
            print("Webui plugin uwsgi execl fails cmd was '%s' error : " % cmd,
                e, file=sys.stderr)
            exit(1)
