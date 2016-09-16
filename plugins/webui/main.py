#-*- coding: utf-8 -*-

import os, os.path
import sys
import shlex
from lodel.plugin import LodelHook
from lodel.settings import Settings
from lodel import buildconf

PLUGIN_PATH = os.path.dirname(__file__)

##@brief Return the root url of the instance
#@warning no trailing slash
def root_url():
    return Settings.sitename


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
        if standalone.lower() == 'true':
            cmd='{uwsgi} --http-socket {addr}:{port} --module \
plugins.webui.run --socket {sockfile}'
            cmd = cmd.format(
                        addr = Settings.webui.listen_address,
                        port = Settings.webui.listen_port,
                        uwsgi= Settings.webui.uwsgicmd,
                        sockfile=sockfile)
            if Settings.webui.virtualenv is not None:
                cmd += " --virtualenv %s" % Settings.webui.virtualenv

        elif Settings.webui.standalone == 'uwsgi':
            cmd = '{uwsgi} --ini ./plugins/webui/uwsgi/uwsgi.ini \
--socket {sockfile}'
            cmd = cmd.format(uwsgi = Settings.webui.uwsgicmd, 
                sockfile = sockfile)
        
        try:
            args = shlex.split(cmd)
            exit(os.execl(args[0], *args))
        except Exception as e:
            print("Webui plugin uwsgi execl fails cmd was '%s' error : " % cmd,
                e, file=sys.stderr)
            exit(1)
