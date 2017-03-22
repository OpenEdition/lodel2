##@brief Contains functions allowing to bootstrap a lodel instance
#
#Typically a bootstrap process consist of settings preload ,
#plugins start and finally settings loading
#
#Assertions that are made in this file :
#- cwd is an instance directory
#- nothing as been done yet (no import, no context etc)
#

import warnings
import os, os.path

import lodel.buildconf
from lodel.context import LodelContext


##@brief Hardcoded configuration dirnames given an instance type
#
#First item is for monosite the second for multisite
#First item for multisite is server conf the second the lodelsites instance
#conf
#
#@note obsolete ! We are preparing a merge of server_conf.d and 
#lodelsites.conf.d
CONFS_DIRNAMES = [
    'conf.d',
    ('server_conf.d', lodel.buildconf.LODELSITE_CONFDIR)]

##@brief Test if current instance is monosite or multisite
#@return if monosite return True else False
def _monosite_test():
    return os.path.isdir('./conf.d')

##@brief Initialize the context class taking care of the instance type (MONO
#or MULTI site)
def _context_initialisation():
    LodelContext.init(
        LodelContext.MONOSITE if _monosite_test() else LodelContext.MULTISITE)

##@brief Return confdir name given instance type and context type
#@param ctx_type : see @ref boostrap()
#@return a configuration directory
#@todo return abspath
def _get_confdir(ctx_type):
    if _monosite_test():
        return CONFS_DIRNAMES[0]
    return CONFS_DIRNAMES[1][1]

    #elif ctx_type == '__loader__':
    #    return CONFS_DIRNAMES[1][0]
    #elif ctx_type == 'lodelsites':
    #    return CONFS_DIRNAMES[1][1]
    #raise ValueError("ctx_type is not one of '__loader__' nor 'lodelsites' \
    #authorized values")

##@brief Return confspec associated with current context & context type
#@param ctx_type str 
#@return None (for default confspecs) or a confspecs dict
def _get_confspec(ctx_type):
    if not _monosite_test():
        LodelContext.expose_modules(globals(), {
            'lodel.plugins.multisite.confspecs': 'multisite_confspecs'})
        return multisite_confspecs.LODEL2_CONFSPECS
    return None
    

##@brief After calling this function you should use your instance as it
#
#@param ctx_type str : ONLY FOR MULTISITE specify wich multisite context to
#bootstrap. The two choices are '__loader__' and 'lodelsites'. Default is 
#__loader__
def bootstrap(ctx_type = None):
    _context_initialisation()
    monosite = _monosite_test()
    if ctx_type is None:
        #Default value
        if not _monosite_test():
            ctx_type = '__loader__'
    elif monosite:
        raise RuntimeError("Not allowed to give a value for ctx_type in a \
MONOSITE instance")
    elif ctx_type not in ['__loader__', 'lodelsites']:
        raise ValueError("ctx_type is not one of '__loader__' nor \
'lodelsites' authorized values")

    custom_confspecs = _get_confspec(ctx_type)

    confdir = _get_confdir(ctx_type)
    if not os.path.isdir(confdir):
        warnings.warn("Bootstraping seems to fail : unable to find confdir \
: %s. Attempt to continue using default values" % confdir)
    
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings_loader')],
        'lodel.plugins.multisite.confspecs': 'multisite_confspecs'})
    
    if ctx_type is not None:
        settings_loader(confdir, custom_confspecs, True) #Append specs
    else:
        settings_loader(confdir, custom_confspecs)
    del(globals()['settings_loader'])

    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})
    
