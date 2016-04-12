#-*- coding: utf-8 -*-

## @page howto_writeplugin Write a plugin howto
#
# @section howto_writeplugin_basicstruct Plugin basic structure
# A plugins is a python package that have to contains 3 files :
#- <code>__init__.py</code>
#- <code>main.py</code> ( defined in @ref lodel.plugin.plugins.MAIN_FILENAME )
#- <code>confspec.py</code> ( defined in
#@ref lodel.plugin.plugins.CONFSPEC_FILENAME )
#
# There is an example plugin in @ref plugins/dummy
#
# @subsection howto_writreplugin_confspec Plugin configuration specification
# First of all a good practice is to preffix all plugin specific configuration
# key with <code>lodel2.plugin.PLUGIN_NAME</code>.
#
# A configuration specification is a dict containing dict containing
# tupe(DEFAULT_VALUE, VALIDATOR). The first level dict keys are sections, and
# the dictionnary contained in it contains conf keys. More information on 
# validators : @ref lodel.settings.validator
# 
# @subsubsection howto_writreplugin_confspec_example Example :
#
#A confspec that matches this peace of configuration file
#<pre>
#[lodel2.plugin.fooplugin]
#hello = ...
#foo = ...
#bar = ...
#</pre>
#would be
#<pre>
#{
#   'lodel2.plugin.fooplugin': {
#                                   'foo': ...,
#                                   'bar': ...,
#                                   'hello': ..., } }
#</pre>
# 

from .hooks import LodelHook
from .plugins import Plugins
