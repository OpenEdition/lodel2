#-*- coding: utf-8 -*-

import os
from lodel.plugin import LodelHook
from lodel.settings import Settings

##@brief uwsgi startup demo
@LodelHook('lodel2_loader_main')
def uwsgi_fork(hook_name, caller, payload):
    if Settings.webui.standalone:
        cmd='uwsgi_python3 --http-socket {addr}:{port} --module run'
        cmd = cmd.format(
                    addr = Settings.webui.listen_address,
                    port = Settings.webui.listen_port)
        exit(os.system(cmd))
