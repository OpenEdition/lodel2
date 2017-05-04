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


from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin': ['LodelHook'],
    'lodel.settings': ['Settings'],
    'lodel.logger': 'logger'})

## @package lodel.plugin.core_hooks
# @brief Lodel2 internal hooks declaration
# @ingroup lodel2_plugins

## @brief Bootstrap hook that checks datasources configuration
# @param hook_name str
# @param caller * : the hook's caller
# @param payload * : data to be given to the hook
# @throw NameError when : a set datasource family name can not be found or a datasource identifier does not match with a configured datasource.
@LodelHook('lodel2_bootstraped')
def datasources_bootstrap_hook(hook_name, caller, payload):
    for ds_name in Settings.datasources._fields:
        ds_conf = getattr(Settings.datasources, ds_name)
        identifier = getattr(ds_conf, 'identifier')

        # Now we are trying to fetch the datasource given the identifier
        ds_family_name, ds_name = identifier.split('.',1)
        try:
            ds_fam = getattr(Settings.datasource, ds_family_name)
        except AttributeError:
            msg = "No datasource family named '%s' found"
            msg %= ds_family_name
            raise NameError(msg)
        try:
            ds = getattr(ds_fam, ds_name)
        except AttributeError:
            msg = "No datasource configured for identifier '%s' found"
            msg %= identifier
            raise NameError(msg)

        log_msg = "Found a datasource named '%s' identified by '%s'"
        log_msg %= (ds_name, identifier)
        logger.debug(log_msg)

## @brief Bootstrap hook that prints debug infos about registered hooks
# @param name str
# @param caller * : the hook's caller
# @param payload * : data to be given to the hook
@LodelHook('lodel2_bootstraped')
def list_hook_debug_hook(name, caller, payload):
    LodelContext.expose_modules(globals(), {
        'lodel.logger': 'logger'})
    hlist = LodelHook.hook_list()
    for name, reg_hooks in hlist.items():
        for hook, priority in reg_hooks:
            logger.debug("{modname}.{funname} is registered as hook \
{hookname} with priority {priority}".format(
                modname = hook.__module__,
                funname = hook.__name__,
                priority = priority,
                hookname = name))
            
        


## @brief Hook that triggers custom methods injection in dynamic classes
# @param caller * : the hook's caller
# @param dynclasses list : a list of classes in which the injection will occur
@LodelHook("lodel2_dyncode_loaded")
def lodel2_plugins_custom_methods(self, caller, dynclasses):
    LodelContext.expose_modules(globals(), {
        'lodel.plugin.plugins': ['CustomMethod']})
    CustomMethod.set_registered(dynclasses)
