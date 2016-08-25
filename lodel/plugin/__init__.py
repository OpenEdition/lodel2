#-*- coding: utf-8 -*-

##@defgroup lodel2_plugins Plugins
#
#Groups all stuff that concerns plugins

## @page plugin_doc Lodel2 plugin documentation
#@ingroup lodel2_plugins
# @section plugin_doc_type Plugin types
#
# Plugins are organized into types. A type specify a behavior. For the moment
# Lodel2 has 4 plugin types :
# - **datasource** : A datasource connector plugin expose CRUD operation on a
#particular datasource
# - **ui** : A user interface plugin provide an interface to lodel2. For the
#moment two ui are implemented
#  - interactive python : the default interface, provides access to LeApi 
#through interactive python interpreter
#  - webui : a plugin providing a web interface to lodel2
# - **session_handler** : A session handler plugin expose functions that handles
#user sessions.
# - **extensions** : An extension plugin can define 2 kinds of objects :
#  - hooks using @ref lodel.plugin.hooks.LodelHook decorator
#  - custom LeApi obect methods using @ref lodel.plugin.plugins.CustomMethod 
#decorator
#
# @subsection Lodel2 scripts
#
# In instances an utility is provided : @ref install.lodel_admin . This 
# utility can be runned as a CLI script 
#<code>usage: lodel_admin.py [-h] [-L] [ACTION] [OPTIONS [OPTIONS ...]]</code>
#
# Each actions is a "lodel2 script". Thoses scripts are parts of plugins.
# @ref lodel2_script "More informations on lodel2 scripting utilities"
#
# @section plugin_doc_struct Common plugin structure
#
# All plugin types has to provide mandatories information in order to be 
# loaded :
#
# - A plugin name
# - A plugin version
# - A confspec indicating where to find the wanted plugin list (for example 
#datasources plugins list are indicated in lodel2.datasource_connectors 
#configuration key see @ref datasource_plugin.DatasourcePlugin::_plist_confspecs ). In
#fact settings MUST begin by loading wanted plugin list in order to build
#a "full" confspec
# - A confspec indicating the plugins allowed settings (will be merged with
#lodel2 confspecs)
# - A loader module filename. This module is imported once settings are
#fully bootstraped and loader. It triggers the module "startup".
#
# In order to provide this informations the develloper can use the plugin's
#package <code>__init__.py</code> file. Some informations are stored in 
#variables in this file. Available variables are documented in 
#@ref plugin_init_specs . Here a list of basics variables :
# - the plugin's name @ref plugins.PLUGIN_NAME_VARNAME
# - the plugin's version @ref plugins.PLUGIN_VERSION_VARNAME
# - the plugin's loader filename @ref plugins.LOADER_FILENAME_VARNAME
# - the plugin's confspec filename @ref plugins.CONFSPEC_FILENAME_VARNAME (
#set this variable only if you want your confspecs to be in a separated file,
#else you can put the confspecs directly in a CONFSPEC variable in the
#<code>__init__.py</code> file see @ref plugins.CONFSPEC_VARNAME )
# - the plugin's type @ref plugins.PLUGIN_TYPE_VARNAME (if not set use 
# @ref plugins.DEFAULT_PLUGIN_TYPE )
# - the plugin's dependencies list @ref plugins.PLUGIN_DEPS_VARNAME
#
# This was the variable specification of the <code>__init__.py</code> file.
#plugins can provide (in the same file) an _activate function ( 
#<code>def _activate(): returns bool</code>) that return True if the plugin
#is activable else False
#
#An example dummy plugin exists in @ref plugins.dummy
#
#@section plugin_doc_childclasses Plugin types implementation
#
# Concretely a plugin type is a child class of @ref plugins.Plugin . Plugin 
# type registration is done automatically using a metaclass for 
# @ref plugins.Plugin : @ref plugins.MetaPlugType . Doing this way
# plugin's type list is automatically generated.
#@note Plugin type handling is not fully automatic because child classes files
#are not automaticaaly imported. We have to add an import instruction into 
#@ref plugin file in order to trigger the registration
#
#The Plugin child class must set the _plist_confspecs class attribute.
#
#More informations :
# - @ref lodel.plugin.datasource_plugin.DatasourcePlugin "DatasourcePlugin"
#  - @ref lodel2_datasources "datasources"
# - @ref lodel.plugin.extensions.Extension "Extensions"
# - @ref lodel.plugin.interface.InterfacePlugin "InterfacePlugin"
# - @ref lodel.plugin.sessionhandler.SessionHandlerPlugin "SessionHandlerPlugin"
#

from .hooks import LodelHook
from .plugins import Plugin, CustomMethod
from .datasource_plugin import DatasourcePlugin
from .sessionhandler import SessionHandlerPlugin
from .interface import InterfacePlugin
from .extensions import Extension
