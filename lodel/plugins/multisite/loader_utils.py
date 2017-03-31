import os
import os.path


##@brief A cache allowing a fast application exposure
#
#This dict contains reference on interface module of each handled site in
#order to quickly call the application (PEP 3333) function of concerned site
FAST_APP_EXPOSAL_CACHE = dict()

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext, ContextError

import lodel.buildconf
##@brief basename of lodelsites site conf folder
LODELSITES_CONFD = lodel.buildconf.LODELSITE_CONFDIR

##@brief Stores the main function of a multisite loader

##@brief Function designed to bootstrap a multisite runner
#
#Handles lodelsites site loading, handled site list fecth & load
#@note called at end of file
#
#@todo evaluate if it is safe to assume that lodelsites_datapath = os.getcwd()
#@todo get rid of hardcoded stuff (like shortname fieldname)
#@todo use the dyncode getter when it will be available (replaced by
#the string SUPERDYNCODE_ACCESSOR.Lodelsite for the moment)
#@return lodelsites instance name
def main():
    #Set current context to reserved loader context
    from lodel import bootstrap
    bootstrap.bootstrap('__loader__')
    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})
    lodelsites_name = Settings.sitename
    lodelsites_datapath = os.path.join(
    	os.path.join(lodel.buildconf.LODEL2VARDIR, lodelsites_name),
	lodel.buildconf.MULTISITE_DATADIR)
    del(globals()['Settings'])
    
    #bootstraping the lodelsites instance
    LodelContext.new(lodelsites_name)
    LodelContext.set(lodelsites_name)
    #in lodelsites context
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings_loader')],
        'lodel.plugins.multisite.confspecs': 'multisite_confspecs',
        'lodel.plugins.multisite.confspecs': 'multisite_confspecs'})

    settings_loader(lodel.buildconf.LODELSITE_CONFDIR,
        multisite_confspecs.LODEL2_CONFSPECS, True)
    del(globals()['settings_loader'])
    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})

    LodelContext.expose_dyncode(globals())

    LodelContext.expose_modules(globals(), {
        'lodel.logger': 'logger',
        'lodel.plugin.hooks': ['LodelHook'],
        'lodel.plugin': ['Plugin']})
    Plugin.load_all()
    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)

    lodelsite_leo = leapi_dyncode.Lodelsite #hardcoded leo name
    LodelContext.expose_modules(globals(), {
        'lodel.leapi.query': ['LeGetQuery'],
    })
    #the line bellow you will find another harcoded thing : the shortname
    #fieldname for a lodelsite
    handled_sites = LeGetQuery(lodelsite_leo, query_filters = [],
        field_list = ['shortname']).execute()
    #Now that we have the handled sitenames list we can go back to
    #loader context and clean it
    if handled_sites is not None:
        LodelContext.set(None)
        for mname in ['LeGetQuery', 'Settings', 'LodelHook', 'Plugin', 'logger']:
            del(globals()[mname])
        #Loading handled sites
        for handled_sitename in [s['shortname'] for s in handled_sites]:
            datapath = os.path.join(lodelsites_datapath, handled_sitename)
            try:
                site_load(datapath) #using default conf.d configuration dirname
            except Exception as e:
                LodelContext.set(None)
                LodelContext.set(lodelsites_name)
                LodelContext.expose_modules(globals(), {
                    'lodel.settings': ['Settings'],
                    'lodel.logger': 'logger'})
                if Settings.debug:
                    logger.critical("Unable to load site %s : %s" % (
                        e, handled_sitename))
                else:
                    raise e
    else:
        logger.warning("No handled sites !")
    LodelContext.set(None)
    return lodelsites_name
    

##@brief Load a site
#
#Apply a common (as MONOSITE) loading process to a site :
#1. Conf preload
#2. Plugins preload
#3. Conf loading
#4. starting plugins & hooks
#@warning At this point we need a uniq identifier for the site (using it
#as key for contexts & FAST_APP_EXPOSAL_CACHE). To achieve this we use
#the data_path basename. It should works for handled sites and for the 
#lodelsites instance
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
def site_load(data_path, confdir_basename = 'conf.d', lodelsites_instance = False):
    #args check
    if confdir_basename != os.path.basename(confdir_basename):
        LodelFatalError('Bad argument given to site_load(). This really \
sux !')
    #Determining uniq sitename from data_path
    data_path = data_path.rstrip('/') #else basename returns ''
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
        settings_preloader(os.path.join('./', confdir_basename), )
    else:
        settings_preloader(os.path.join('./', confdir_basename))
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
    #lodel2 multisite instances are loaded and ready to run


