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
#@todo remove hardcoded app name (need a better abstraction or a really
#generic multiinstance runner)
#@return lodelsites instance name
def main(handled_sites_may_not_load = False):
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
        LodelContext.expose_modules(globals(), {
            'lodel.bootstrap': ['site_preload', 'site_load']})
        for mname in ['LeGetQuery', 'Settings', 'LodelHook', 'Plugin', 'logger']:
            del(globals()[mname])
        #Loading handled sites
        for handled_sitename in [s['shortname'] for s in handled_sites]:
            datapath = os.path.join(lodelsites_datapath, handled_sitename)
            try:
                site_preload(datapath) #using default conf.d configuration dirname
                site_load(datapath)
                #
                # HARDCODED APP NAME
                #
                populate_fast_app_cache(datapath, 'lodel.plugins.webui.run')
            except Exception as e:
                LodelContext.set(None)
                LodelContext.set(lodelsites_name)
                LodelContext.expose_modules(globals(), {
                    'lodel.settings': ['Settings'],
                    'lodel.logger': 'logger'})
                if Settings.debug or handled_sites_may_not_load:
                    logger.critical("Unable to load site %s : %s" % (
                        e, handled_sitename))
                else:
                    raise e
    else:
        logger.warning("No handled sites !")
    LodelContext.set(None)
    return lodelsites_name
    
##@brief Add an app to FAST_APP_EXPOSAL_CACHE
#@param data_path str : instance data_path (used to extract the sitename !)
#@param app_name str : application name (like lodel.plugins.webui.run)
def populate_fast_app_cache(data_path, app_name):
    ctx_name = os.path.basename(data_path)
    LodelContext.set(ctx_name)
    FAST_APP_EXPOSAL_CACHE[ctx_name] = LodelContext.module(app_name)
    LodelContext.set(None)

