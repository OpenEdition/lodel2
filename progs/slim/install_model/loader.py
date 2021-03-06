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


##@brief Lodel2 loader script
#
#@note If you want to avoid settings loading you can set the environment
#variable LODEL2_NO_SETTINGS_LOAD (see @ref install.lodel_admin.update_plugin_discover_cache()
#
# @note In tests case, you can pass the path to write results file, context_tests.log 
# It has to be at first, otherwise it will not be taken 
# and the default one, current directory, will be used.

import sys, os, os.path
#
# Bootstraping
#
LODEL2_LIB_ABS_PATH = None
if LODEL2_LIB_ABS_PATH is not None:
    if not os.path.isdir(LODEL2_LIB_ABS_PATH):
        print("FATAL ERROR : the LODEL2_LIB_ABS_PATH variable in loader.py is \
not correct : '%s'" % LODEL2_LIB_ABS_PATH, file=sys.stderr)
    sys.path.append(LODEL2_LIB_ABS_PATH)

try:
    import lodel
except ImportError as e:
    print("Unable to load lodel module. exiting...")
    print(e)
    exit(1)

#Set context to MONOSITE
from lodel.context import LodelContext
LodelContext.init()

if 'LODEL2_NO_SETTINGS_LOAD' not in os.environ:
    #
    # Loading settings
    #
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings')]})
    if not settings.started():
        settings('conf.d')
    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})
    
    #Starts hooks
    LodelContext.expose_modules(globals(), {
        'lodel.plugin': ['LodelHook'],
	'lodel.plugin.core_hooks': 'core_hooks',
	'lodel.plugin.core_scripts': 'core_scripts'})

def start():
    #Load plugins
    LodelContext.expose_modules(globals(), {
        'lodel.logger': 'logger',
        'lodel.plugin': ['Plugin']})
    logger.debug("Loader.start() called")
    Plugin.load_all()
    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)


if __name__ == '__main__':

    start()
    if Settings.runtest:
        import unittest
        import tests
        loader = unittest.TestLoader()
        test_dir = os.path.join(LODEL2_LIB_ABS_PATH, 'tests')
        suite = loader.discover(test_dir, pattern='test*.py')
        if ((len(sys.argv) > 1) and (sys.argv[1].startswith('-')) is False):
            dpath = sys.argv[1]
        else:
            dpath = '.'
        with open(sys.argv[1]+'/context_tests.log', 'w') as logfile:
            tests_res = unittest.TextTestRunner(
                logfile,
                failfast = '-f' in sys.argv,
                verbosity = 2 if '-v' in sys.argv else 1).run(suite)
        if tests_res.wasSuccessful():
            exit(0)
        else:
            exit(1)

    lodel = LodelContext.get()
    import leapi_dyncode as dyncode
    lodel.dyncode = dyncode
    LodelHook.call_hook('lodel2_dyncode_bootstraped', '__main__', None)
    LodelHook.call_hook('lodel2_loader_main', '__main__', None)

    #Run interative python
    import code
    print("""
     Running interactive python in Lodel2 %s instance environment

"""%Settings.sitename)
    code.interact(local=locals())
