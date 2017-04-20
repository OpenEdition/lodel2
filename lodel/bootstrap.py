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
#@todo delete the argument
#@todo delete this function
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
    
##@brief Preload a site
#
#Apply a common (as MONOSITE) loading process to a site :
#1. Conf preload
#2. Plugins preload
#3. Conf loading
#
#4. starting plugins & hooks
#@warning At this point we need a uniq identifier for the site (using it
#as key for contexts & FAST_APP_EXPOSAL_CACHE). To achieve this we use
#the data_path basename. It should works for handled sites and for the 
#lodelsites instance
#@warning may only work for handled sites in a multisite context
#@param data_path str : path to the datas directory (containing the confdir)
#@param confdir_basename str : the basename of the site confdir
#@param lodelsites_instance bool : if true we are loading the lodelsites
#instance of the multisite (allow to load the good confspecs)
#
#@todo For now the interface plugin name for sites is hardcoded (set to
#webui). It HAS TO be loaded from settings. But it is a bit complicated, 
#we have to get the plugin's module name abstracted from context :
#lodel.something but if we ask directly to Plugin class the module name
#it will return something like : lodelsites.sitename.something...
#
#@todo there is a quick & dirty workarround with comments saying that it
#avoid context escape via hooks. We have to understand why and how and then
#replace the workarround by a real solution !
#@todo check if it works with monosite context !
#@todo change data_path argument to sitename and determine datapath from it
def site_preload(data_path, confdir_basename = 'conf.d', lodelsites_instance = False):
    #args check
    if confdir_basename != os.path.basename(confdir_basename):
        LodelFatalError('Bad argument given to site_load(). This really \
sux !')
    #Determining uniq sitename from data_path
    data_path = os.path.dirname(data_path).rstrip('/') #else basename returns ''
    ctx_name = os.path.basename(data_path)
    if not os.path.exists(data_path) or not os.path.isdir(data_path):
        LodelContext.expose_modules(globals(), {
            'lodel.exceptions': ['LodelFatalError']})
        raise LodelFatalError("A site named '%s' was found in the DB but not on the FS (expected to found it in '%s'!!!" % (os.path.basename(data_path), data_path))
    #Immediately switching to the context
    LodelContext.new(ctx_name)
    LodelContext.set(ctx_name)
    os.chdir(data_path) #Now the confdir is ./$condir_basename
    #Loading settings for current site
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings_preloader')]})
    if settings_preloader.started():
        msg = 'Settings seems to be allready started for "%s". \
This should not append !' % ctx_name
        #switch back to loader context in order to log & raise
        LodelContext.set(None)
        logger.critical(msg)
        raise LodelFatalError(msg)
    if lodelsites_instance:
        #fetching custom confspec
        custom_confspec = _get_confspec("dummy_argument_is_obsolete")
        settings_preloader(os.path.join('./', confdir_basename),
            custom_confspec, True)
    else:
        settings_preloader(os.path.join('./', confdir_basename))
    LodelContext.set(None)
    return

##@brief End a site loading process (load plugins & hooks)
#@param data_path str : site data path (used to extract the sitename !!)
#@todo change data_path argument to sitename
def site_load(data_path):
    ctx_name = os.path.basename(data_path)
    LodelContext.set(ctx_name)
    #
    #Loading hooks & plugins
    #
    LodelContext.expose_modules(globals(), {
        'lodel.plugin': ['Plugin', 'LodelHook'],
        'lodel.logger': 'logger',
        'lodel.plugin.core_hooks': 'core_hooks',
        'lodel.plugin.core_scripts': 'core_scripts'
    })
    Plugin.load_all() #Then all plugins & hooks are loaded
    #triggering dyncode datasource instanciations
    LodelHook.call_hook('lodel2_plugins_loaded', '__main__', None)
    #triggering boostrapped hook
    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)
    #Populating FAST_APP_EXPOSAL_CACHE
    #
    #WARNING !!!! Hardcoded interface name ! Here we have to find the 
    #interface plugin name in order to populate the cache properly
    FAST_APP_EXPOSAL_CACHE[ctx_name] = LodelContext.module(
        'lodel.plugins.webui.run')
    #a dirty & quick attempt to fix context unwanted exite via
    #hooks
    for name in ( 'LodelHook', 'core_hooks', 'core_scripts',
            'Settings', 'settings', 'logger', 'Plugin'):
        del(globals()[name])
    #site fully loaded, switching back to loader context
    LodelContext.set(None)

##@brief Fetch handled sites name
#@warning assert that a full __loader__ context is ready and that the
#multisite context is preloaded too
#@warning hardcoded Lodelsite leo name and shortname fieldname
#@todo attempt to delete hardcoded leo name
#@todo attempt to delete hardcoded fieldname
def get_handled_sites_name():
    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})
    lodelsites_name = Settings.sitename
    LodelContext.set(lodelsites_name)
    lodelsite_leo = leapi_dyncode.Lodelsite #hardcoded leo name
    LodelContext.expose_modules(globals(), {
        'lodel.leapi.query': ['LeGetQuery'],
    })
    handled_sites = LeGetQuery(lodelsite_leo, query_filters = [],
        field_list = ['shortname']).execute()
    if handled_sites is None:
        return []
    res = [ s['shortname'] for s in handled_sites]
    del(globals()['LeGetQuery'])
    del(globals()['Settings'])
    LodelContext.set(None)
    return res
    
