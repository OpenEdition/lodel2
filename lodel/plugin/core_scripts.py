from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.scripts': 'lodel_script'})

##@package lodel.plugin.core_scripts
#@brief Lodel2 internal scripts declaration
#@ingroup lodel2_plugins
#@ingroup lodel2_script


##@brief Implements lodel_admin.py **discover-plugin** action
#@ingroup lodel2_plugins
#@ingroup lodel2_script
#
#In depth directory scan to find plugins in order to build a plugin list.
class DiscoverPlugin(lodel_script.LodelScript):
    _action = 'discover-plugin'
    _description = 'Walk through given folders looking for plugins'
    
    @classmethod
    def argparser_config(cls, parser):
        #parser.add_argument('-d', '--directory',
        parser.add_argument('PLUGIN_PATH',
            help="Directory to walk through looking for lodel2 plugins",
            nargs='+')
        parser.add_argument('-l', '--list-only', default=False,
            action = 'store_true',
            help="Use this option to print a list of discovered plugins \
without modifying existing cache")

    @classmethod
    def run(cls, args):
        from lodel.plugin.plugins import Plugin
        if args.PLUGIN_PATH is None or len(args.PLUGIN_PATH) == 0:
            cls.help_exit("Specify a least one directory")
        no_cache = args.list_only
        res = Plugin.discover(args.PLUGIN_PATH, no_cache)
        print("Found plugins in : %s" % ', '.join(args.PLUGIN_PATH))
        for pname, pinfos in res['plugins'].items():
            print("\t- %s(%s) in %s" % (
                pname, pinfos['version'], pinfos['path']))
            
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

