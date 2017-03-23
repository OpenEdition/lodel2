import os
import shlex
from lodel.context import LodelContext
import lodel.buildconf

LodelContext.expose_modules(globals(), {
    'lodel.plugin.hooks': ['LodelHook'],
})

##@brief Starts uwsgi in background using settings
@LodelHook('lodel2_loader_main')
def uwsgi_fork(hook_name, caller, payload):
    
    sockfile = os.path.join(lodel.buildconf.LODEL2VARDIR, 'uwsgi_sockets/')
    if not os.path.isdir(sockfile):
        os.mkdir(sockfile)
    sockfile = os.path.join(sockfile, 'uwsgi_lodel2_multisite.sock')
    logfile = os.path.join(
        lodel.buildconf.LODEL2LOGDIR, 'uwsgi_lodel2_multisite.log')
    
    #Switching to __loader__ context
    print("PASS1")
    LodelContext.set(None)
    print("PASS2")
    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})
    print("PASS3")

    cmd='{uwsgi} --plugin python3 --http-socket {addr}:{port} --module \
lodel.plugins.multisite_web.run --socket {sockfile} --logto {logfile} -p {uwsgiworkers}'
    cmd = cmd.format(
                addr = Settings.server.listen_address,
                port = Settings.server.listen_port,
                uwsgi= Settings.server.uwsgicmd,
                sockfile=sockfile,
                logfile = logfile,
                uwsgiworkers = Settings.server.uwsgi_workers)
    if Settings.server.virtualenv is not None:
        cmd += " --virtualenv %s" % Settings.webui.virtualenv

    print("PASS4")
    try:
        args = shlex.split(cmd)
        print("Running %s" % cmd)
        exit(os.execl(args[0], *args))
    except Exception as e:
        print("Webui plugin uwsgi execl fails cmd was '%s' error : " % cmd,
            e, file=sys.stderr)
        exit(1)

