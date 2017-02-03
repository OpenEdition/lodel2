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
try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext

from lodel import buildconf

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

LodelContext.expose_modules(globals(), {
    'lodel.settings': ['Settings']})

##@brief Starts uwsgi in background using settings
def uwsgi_fork():
    
    sockfile = os.path.join(buildconf.LODEL2VARDIR, 'uwsgi_sockets/')
    if not os.path.isdir(sockfile):
        os.mkdir(sockfile)
    sockfile = os.path.join(sockfile, 'uwsgi_lodel2_multisite.sock')
    logfile = os.path.join(
        buildconf.LODEL2LOGDIR, 'uwsgi_lodel2_multisite.log')
        
    cmd='{uwsgi} --plugin python3 --http-socket {addr}:{port} --module \
lodel.plugins.multisite.run --socket {sockfile} --logto {logfile} -p {uwsgiworkers}'
    cmd = cmd.format(
                addr = Settings.server.listen_address,
                port = Settings.server.listen_port,
                uwsgi= Settings.server.uwsgicmd,
                sockfile=sockfile,
                logfile = logfile,
                uwsgiworkers = Settings.server.uwsgi_workers)
    if Settings.server.virtualenv is not None:
        cmd += " --virtualenv %s" % Settings.webui.virtualenv

    try:
        args = shlex.split(cmd)
        print("Running %s" % cmd)
        exit(os.execl(args[0], *args))
    except Exception as e:
        print("Webui plugin uwsgi execl fails cmd was '%s' error : " % cmd,
            e, file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    uwsgi_fork()
        
