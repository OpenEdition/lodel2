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

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext, ContextError

import lodel.buildconf #safe even outside contexts
from lodel.plugins.multisite.loader_utils import main, site_load, FAST_APP_EXPOSAL_CACHE #UNSAFE ??!!
lodelsites_name = main()
LodelContext.set(lodelsites_name)
FAST_APP_EXPOSAL_CACHE[lodelsites_name] = LodelContext.module(
    'lodel.plugins.webui.run')
LodelContext.set(None)

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
    LodelContext.set(None) #Ensure context switching
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

