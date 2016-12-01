#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#RUN FROM GIT REPO ROOT

import sys
sys.path.append('.')

from plugins.multisite.module_wrapper import *
import lodel

init_module()
res = new_site_module("foobar")

print(res)
print(dir(res))
print(res.auth)
print(dir(res.plugin))
print(dir(res.plugin.plugins))

#for modname in sorted(sys.modules.keys()):
#    print(modname)
