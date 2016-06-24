#-*- coding: utf-8 -*-

from lodel.plugin import LodelHook
from lodel.settings import Settings
from lodel import logger

##@package lodel.plugin.core_hooks
#@brief Lodel2 internal hooks declaration

##@brief Bootstrap hook to check datasources configuration
@LodelHook('lodel2_bootstraped')
def datasources_bootstrap_callaback(hook_name, caller, payload):
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

@LodelHook("lodel2_dyncode_loaded")
def lodel2_plugins_custom_methods(self, caller, dynclasses):
    from lodel.plugin.plugins import CustomMethod
    CustomMethod.set_registered(dynclasses)
