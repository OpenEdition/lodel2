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


import os
import os.path
import warnings

#This file expose common function to process a wsgi request and the
#uWSGI application callback


#preloading all instances
FAST_APP_EXPOSAL_CACHE = dict()

LODEL2_INSTANCES_DIR = '.'
EXCLUDE_DIR = {'conf.d', '__pycache__'}

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext, ContextError

LodelContext.init(LodelContext.MULTISITE)
LodelContext.set(None) #Loading context creation

#Multisite instance settings loading
CONFDIR = os.path.join(os.getcwd(), 'conf.d')
if not os.path.isdir(CONFDIR):
    warnings.warn('%s do not exists, default settings used' % CONFDIR)
LodelContext.expose_modules(globals(), {
    'lodel.settings.settings': [('Settings', 'settings')],
    'lodel.plugins.multisite.confspecs': 'multisite_confspecs'})
if not settings.started():
    settings('./conf.d', multisite_confspecs.LODEL2_CONFSPECS)

#Fetching insrtance list from subdirectories
lodelsites_list = [ os.path.realpath(os.path.join(LODEL2_INSTANCES_DIR,sitename)) 
    for sitename in os.listdir(LODEL2_INSTANCES_DIR)
    if os.path.isdir(sitename) and sitename not in EXCLUDE_DIR]

#Bootstraping instances
for lodelsite_path in lodelsites_list:
    ctx_name = LodelContext.from_path(lodelsite_path)
    #Switch to new context
    LodelContext.set(ctx_name)
    os.chdir(lodelsite_path)
    # Loading settings
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings')]})
    if not settings.started():
        settings('./conf.d')
    LodelContext.expose_modules(globals(), {'lodel.settings': ['Settings']})

    # Loading hooks & plugins
    LodelContext.expose_modules(globals(), {
        'lodel.plugin': ['LodelHook'],
        'lodel.plugin.core_hooks': 'core_hooks',
        'lodel.plugin.core_scripts': 'core_scripts'
    })

    #Load plugins
    LodelContext.expose_modules(globals(), {
        'lodel.logger': 'logger',
        'lodel.plugin': ['Plugin']})
    logger.debug("Loader.start() called")
    Plugin.load_all()
    #Import & expose dyncode
    LodelContext.expose_dyncode(globals())
    #Next hook triggers dyncode datasource instanciations
    LodelHook.call_hook('lodel2_plugins_loaded', '__main__', None)
    #Next hook triggers call of interface's main loop
    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)
    #FAST_APP_EXPOSAL_CACHE populate
    FAST_APP_EXPOSAL_CACHE[ctx_name] = LodelContext.module(
    	'lodel.plugins.webui.run')
    LodelContext
    #a dirty & quick attempt to fix context unwanted exite via
    #hooks
    for name in ( 'LodelHook', 'core_hooks', 'core_scripts',
            'Settings', 'settings', 'logger', 'Plugin'):
        del(globals()[name])
    #switch back to loader context
    LodelContext.set(None)

#
# From here lodel2 multisite instances are loaded and ready to run
#


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

