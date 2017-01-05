import operator
from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.scripts': 'lodel_script'})

##@package lodel.plugin.core_scripts
#@brief Lodel2 internal scripts declaration
#@ingroup lodel2_plugins
#@ingroup lodel2_script


##@brief Implements lodel_admin.py list-plugins action
#@ingroup lodel2_plugins
#@ingroup lodel2_script
#
class ListPlugins(lodel_script.LodelScript):
    _action = 'list-plugins'
    _description = "List all installed plugins"

    @classmethod
    def argparser_config(cls, parser):
        parser.add_argument('-v', '--verbose',
            help="Display more informations on installed plugins",
            action='store_true')
        parser.add_argument('-c', '--csv',
            help="Format output in CSV format",
            action='store_true')

    @classmethod
    def run(cls, args):
        from lodel.plugin.plugins import Plugin
        plist = Plugin.discover()
        if args.csv:
            if args.verbose:
                res = "name,version,path\n"
                fmt = "%s,%s,%s\n"
            else:
                res = "name,version\n"
                fmt = "%s,%s\n"
        else:
            res = "Installed plugins list :\n"
            if args.verbose:
                fmt = "\t- %s(%s) in %s\n"
            else:
                fmt = "\t- %s(%s)\n"
        for pname in sorted(plist.keys()):
            pinfos = plist[pname]
            if args.verbose:
                res += fmt % (
                    pinfos['name'], pinfos['version'], pinfos['path'])
            else:
                res += fmt % (pinfos['name'], pinfos['version'])
        print(res)

##@brief Implements lodel_admin.py **hooks-list** action
#@ingroup lodel2_script
#@ingroup lodel2_hooks
class ListHooks(lodel_script.LodelScript):
    _action = 'hooks-list'
    _description = 'Generate a list of registered hooks once instance started'

    @classmethod
    def argparser_config(cls, parser):
        pass

    @classmethod
    def run(cls, args):
        import loader
        loader.start()
        from lodel.plugin.hooks import LodelHook
        hlist = LodelHook.hook_list()
        print("Registered hooks : ")
        for name in sorted(hlist.keys()):
            print("\t- %s is registered by :" % name)
            for hfun, priority in hlist[name]:
                msg = "\t\t- {modname}.{funname} with priority : {priority}"
                print(msg.format(
                    modname = hfun.__module__,
                    funname = hfun.__name__,
                    priority = priority))
            print("\n")

