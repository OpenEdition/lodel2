# -*- coding: utf-8 -*-
import os
import sys
import shlex
import warnings

##@brief Preloader for a multisite process
#
#This loader is a kind of fake loader. In fact it only read configurations
#for the multisite instance and then run a UWSGI process that will run
#the run.py file.
#
#If you want to see the "real" multisite loading process see
#@ref lodel/plugins/multisite/run.py file
#
#@par Implementation details 
#Here we have to bootstrap a minimal __loader__ context in order
#to be able to load the settings
#
#This file (once bootstraped) start a new process for uWSGI. uWSGI then
#run lodel.plugins.multisite.run.application function
#@note the uwsgi process in started using the execl function when UWSGI
#will exit this process will stop too
#
from lodel import buildconf
from lodel import bootstrap
bootstrap.bootstrap('__loader__')

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext


LodelContext.expose_modules(globals(), {
    'lodel.plugin.hooks': ['LodelHook'],
})

#If an interface that execl to run was loaded it will be run by following
#hook
LodelHook.call_hook('multisite_execl_interface', '__main__', None)

#Nothing appened, running default ipython interface
#The interface as to be run by execl to go out of this partial context
PYTHON_EXC = '/usr/bin/python3'
RUNNER_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'run.py')
cmd = '%s "%s"' % (PYTHON_EXC, RUNNER_FILE)
try:
    args = shlex.split(cmd)
    print("\n\nEND LOADER MULTISITE, execl\n\n")
    exit(os.execl(args[0], *args))
except Exception as e:
    print("Multisite std interface execl fails. Command was : '%s' error \
: %s" % (cmd, e), file=sys.stderr)
    exit(1)

