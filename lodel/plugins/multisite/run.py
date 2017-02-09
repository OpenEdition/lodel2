# -*- coding: utf-8 -*-
import os
import os.path
import warnings

##@brief File designed to be executed by an UWSGI process in order to
#run a multisite instance process
#
#@warning In this module we have to be VERY carrefull about module exposure !
#in fact here we will go through every context at least once and the globals
#will be shared all among the module. So ANY exposed module will be accessible
#for a short time outside its context !! A good way be protected about that
#is to del(globals()[exposed_module_name]) after use. But it's really not
#sure that this way of doing is a real safe protection !
#
#@par Expected context when called
#- cwd has to be the lodelsites directory (the directory containing the 
#conf.d folder)
#
#This file is divided in two blocks :
#
#@par Run at load
#The main function will be called at import.
#This piece of code handles :
#- loading the lodelsites site (the site that handles sites ;) )
#- fetch the list of handled lodel sites
#- loading the whole list of lodel sites
#
#@par WSGI processing
#The other functions are here to handles WSGI request. The entry function
#is application(), following the PEP 3333 specifications

#
#   Constants declarations
#

##@brief basename of multisite process conf folder
#@todo find a better place to declare it
SERVER_CONFD = 'server.conf.d' #Should be accessible elsewhere
##@brief basename of lodelsites site conf folder
#@todo find a better place to declare it
LODELSITES_CONFD = 'lodelsites.conf.d' #Should be accessible elsewhere

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

import os.path
import lodel.buildconf #safe even outside contexts


##@brief Function that will run at import time
#
#Handles lodelsites site loading, handled site list fecth & load
#@note called at end of file
#
#@todo evaluate if it is safe to assume that lodelsites_datapath = os.getcwd()
#@todo get rid of hardcoded stuff (like shortname fieldname)
#@todo use the dyncode getter when it will be available (replaced by
#the string SUPERDYNCODE_ACCESSOR.Lodelsite for the moment)
def main():
    LodelContext.init(LodelContext.MULTISITE)
    #Set current context to reserved loader context
    LodelContext.set(None)
    LodelContext.expose_modules(globals(), {
        'lodel.logger': 'logger',
        'lodel.exceptions': ['LodelFatalError'],
    })
    
    CONFDIR = os.path.join(os.getcwd(), SERVER_CONFD)
    if not os.path.isdir(CONFDIR):
        logger.critical('Multisite process bootstraping fails : unable to \
find the %s folder' % SERVER_CONFD)
    
    #Settings bootstraping for mutlisite process
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings')],
        'lodel.plugins.multisite.confspecs': 'multisite_confspecs'})
    settings(CONFDIR, mutisite_confspecs.LODEL2_CONFSPECS)
    #Loading settings
    del(globals()['settings']) #useless but may be safer
    #Exposing "real" settings object in loader context
    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})
    #Fetching lodelsites informations
    lodelsites_name = Settings.sites_handler_name
    #Following path construction is kind of dirty ! We should be able
    #to assume that the lodelsites_datapath == os.getcwd()....
    lodelsites_datapath = os.path.join(LODEL2VARDIR, lodelsites_name)
    #loading lodelsites site
    load_site(lodelsites_datapath, LODELSITES_CONFD)

    #Fetching handled sites list 
    #WARNING ! Here we assert that context name == basename(lodelsites_datapath)
    LodelContext.set(lodelsites_name)
    #in lodelsites context
    Lodelsite_leo = SUPERDYNCODE_ACCESSOR.Lodelsite #hardcoded leo name
    LodelContext.expose_modules(globals(), {
        'lodel.leapi.query': ['LeGetQuery'],
    })
    #the line bellow you will find another harcoded thing : the shortname
    #fieldname for a lodelsite
    handled_sites = LeGetQuery(lodelsite_leo, query_filters = [],
        field_list = ['shortname'])
    #Now that we have the handled sitenames list we can go back to
    #loader context and clean it
    LodelContext.set(None)
    for mname in ['LeGetQuery', 'Settings']:
        del(globals()[mname])
    #Loading handled sites
    for handled_sitename in [s['shortname'] for s in handled_sites]:
        datapath = os.path.join(lodelsites_datapath, handled_sitename)
        site_load(datapath) #using default conf.d configuration dirname
    

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
def site_load(data_path, confdir_basename = 'conf.d'):
    #args check
    if confdir_basename != os.path.basename(confdir_basename):
        LodelFatalError('Bad argument given to site_load(). This really \
sux !')
    #Determining uniq sitename from data_path
    data_path = data_path.rstrip('/') #else basename returns ''
    ctx_name = os.path.basename(data_path)
    #Immediately switching to the context
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
    settings(os.path.join('./', confdir_basename))
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


##@brief Utility function to return quickly an error
def http_error(env, start_response, status = '500 internal server error', \
        extra = None):
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    msg = status
    if extra is not None:
        msg = extra
    return [msg.encode('utf-8')]


##@brief utility function to extract site id from an url
#@param url str : 
def site_id_from_url(url):
    res = ''
    for c in url[1:]:
        if c == '/':
            break
        res += c
    if len(res) == 0:
        return None
    return res

##@brief This method is run in a child process by the handler
def application(env, start_response):
    #Attempt to load a context
    site_id = site_id_from_url(env['PATH_INFO'])
    if site_id is None:
        #It can be nice to provide a list of instances here
        return http_error(env, start_response, '404 Not Found')
    try:
        LodelContext.set(site_id)
        #We are in the good context

    except ContextError as e:
        print(e)
        return http_error(env, start_response, '404 Not found',
            "No site named '%s'" % site_id)
    #Calling webui
    return FAST_APP_EXPOSAL_CACHE[site_id].application(env, start_response)
    #LodelContext.expose_modules(globals(), {
    #    'lodel.plugins.webui.run': ['application']})
    #return application(env, start_response)

#calling the main function
main()
