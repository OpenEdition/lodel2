#-*- coding: utf-8 -*-

## @page howto_writeplugin Write a plugin howto
#
# @section howto_writeplugin_basicstruct Plugin basic structure
# A plugins is a python package that have to contains 3 files :
# - <code>__init__.py</code>
# - <code>main.py</code> ( defined in @ref lodel.plugin.plugins.MAIN_NAME )
# - <code>confspec.py</code> ( defined in @ref lodel.plugin.plugins.CONFSPEC_NAME )
#
# 

from .hooks import LodelHook
from .plugins import Plugins
