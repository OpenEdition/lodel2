#-*- coding: utf-8 -*-

import os, os.path
from lodel.plugin import LodelHook
from lodel.settings import Settings

PLUGIN_PATH = os.path.dirname(__file__)

##@brief Return the root url of the instance
def root_url():
    return Settings.sitename


##@brief uwsgi startup demo
@LodelHook('lodel2_loader_main')
def uwsgi_fork(hook_name, caller, payload):
    if Settings.webui.standalone:
        cmd='uwsgi_python3 --http-socket {addr}:{port} --module plugins.webui.run'
        cmd = cmd.format(
                    addr = Settings.webui.listen_address,
                    port = Settings.webui.listen_port)
        exit(os.system(cmd))
