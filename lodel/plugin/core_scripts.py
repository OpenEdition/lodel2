import operator
import shutil
import tempfile
import os, os.path
from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.scripts': 'lodel_script',
    'lodel.logger': 'logger'})

##@package lodel.plugin.core_scripts
#@brief Lodel2 internal scripts declaration
#@ingroup lodel2_plugins
#@ingroup lodel2_script


##@brief Implements lodel_admin.py list-plugins action
#@ingroup lodel2_plugins
#@ingroup lodel2_script
#
class ListPlugins(lodel_script.LodelScript):
    _action = 'plugins-list'
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
        import lodel.plugin.plugins
        from lodel.plugin.plugins import Plugin
        if args.verbose:
            #_discover do not returns duplicated names
            tmp_plist = Plugin._discover(lodel.plugin.plugins.PLUGINS_PATH)
            plist = []
            #ordering the list by plugin's name
            for pname in sorted(set([d['name'] for d in tmp_plist])):
                for pinfos in tmp_plist:
                    if pinfos['name'] == pname:
                        plist.append(pinfos)
        else:
            pdict = Plugin.discover()
            #casting to a list ordered by names
            plist = []
            for pname in sorted(pdict.keys()):
                plist.append(pdict[pname])
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
        for pinfos in plist:
            if args.verbose:
                res += fmt % (
                    pinfos['name'], pinfos['version'], pinfos['path'])
            else:
                res += fmt % (pinfos['name'], pinfos['version'])
        print(res)


##@brief Handle install & uninstall of lodel plugins
class PluginManager(lodel_script.LodelScript):
    _action = 'plugins'
    _description = "Install/Uninstall plugins"

    @classmethod
    def argparser_config(cls, parser):
        parser.add_argument('-u', '--uninstall',
            help="Uninstall specified plugin",
            action='store_true')
        parser.add_argument('-c', '--clean',
            help="Uninstall duplicated plugins with smallest version number",
            action="store_true")
        parser.add_argument('-n', '--plugin-name', nargs='*',
            default = list(),
            help="Indicate a plugin name to uninstall",
            type=str)
        parser.add_argument('-f', '--file', nargs='*',
            default = list(),
            help="Specify a tarball containing a plugin to install",
            type=str)
        parser.add_argument('-d', '--directory', nargs='*',
            default = list(),
            help="Specify a plugin by its directory",
            type=str)

    @classmethod
    def run(cls, args):
        if args.clean:
            if args.uninstall or len(args.directory) > 0 or len(args.file) > 0:
                raise RuntimeError("When using -c --clean option you can \
only use option -n --name to clean plugins with specified names")
            return cls.clean(args)
        if args.uninstall:
            return cls.uninstall(args)
        return cls.install(args)
    
    ##@brief Handles plugins install
    @classmethod
    def install(cls, args):
        import lodel.plugin.plugins
        from lodel.plugin.plugins import Plugin
        from lodel.plugin.exceptions import PluginError
        if len(args.plugin_name) > 0:
            raise RuntimeError("Unable to install a plugin from its name !\
We do not know where to find it...")
        plist = Plugin.discover()
        errors = dict()
        if len(args.file) > 0:
            raise NotImplementedError("Not supported yet")
        
        plugins_infos = {}
        for cur_dir in args.directory:
            try:
                res = Plugin.dir_is_plugin(cur_dir, assert_in_package = False)
                if res is False:
                    errors[cur_dir] = PluginError("Not a plugin")
                else:
                    plugins_infos[res['name']] = res
            except Exception as e:
                errors[cur_dir] = e
        #Abording because of previous errors
        if len(errors) > 0:
            msg = "Abording installation because of following errors :\n"
            for path, expt in errors.items():
                msg += ("\t- For path '%s' : %s\n" % (path, expt))
            raise RuntimeError(msg)
        #No errors continuing to install
        for pname, pinfos in plugins_infos.items():
            if pname in plist:
                #Found an installed plugin with the same name
                #Cehcking both versions
                if plist[pname]['version'] == pinfos['version']:
                    errors[pinfos['path']] = 'Abording installation of %s \
found in %s because it seems to be allready installed in %s' % (
    pname, pinfos['path'], plist[pname]['path'])
                    continue
                if plist[pname]['version'] > pinfos['version']:
                    errors[pinfos['path']] = 'Abording installation of %s \
found in %s because the same plugins with a greater version seems to be \
installed in %s' % (pname, pinfos['path'], plist[pname]['path'])
                    continue
                logger.info("Found a plugin with the same name but with an \
inferior version. Continuing to install")
            #Checking that we can safely copy our plugin
            dst_path = os.path.join(lodel.plugin.plugins.PLUGINS_PATH,
                os.path.basename(os.path.dirname(pinfos['path'])))
            orig_path = dst_path
            if os.path.isdir(dst_path):
                dst_path = tempfile.mkdtemp(
                    prefix = os.path.basename(dst_path)+'_',
                    dir = lodel.plugin.plugins.PLUGINS_PATH)
                logger.warning("A plugin allready exists in %s. Installing \
in %s" % (orig_path, dst_path))
                shutil.rmtree(dst_path)
                
            #Installing the plugin
            shutil.copytree(pinfos['path'], dst_path, symlinks = False)
            print("%s(%s) installed in %s" % (
                pname, pinfos['version'], dst_path))
        if len(errors) > 0:
            msg = "Following errors occurs during instalation process :\n"
            for path, error_msg in errors.items():
                msg += "\t- For '%s' : %s" % (path, error_msg)
            print(msg)
    
    ##@brief Handles plugins uninstall
    @classmethod
    def uninstall(cls, args):
        raise NotImplementedError("Not yet implemented")

    ##@brief Handles plugins clean
    @classmethod
    def clean(cls, args):
        import lodel.plugin.plugins
        from lodel.plugin.plugins import Plugin
        if len(args.file) > 0:
            raise RuntimeError("Cannot specify plugins to uninstall using \
-f --file option. You have to use -d --directory or -n --name")
        if len(args.plugin_name) > 0:
            names = args.plugin_name
        else:
            names = list(Plugin.discover().keys())
        #_dicover do not remove duplicated names
        full_list = Plugin._discover(lodel.plugin.plugins.PLUGINS_PATH)
        #Casting into a dict with list of plugins infos
        pdict = dict()
        for pinfos in full_list:
            if pinfos['name'] in names:
                if pinfos['name'] in pdict:
                    pdict[pinfos['name']].append(pinfos)
                else:
                    pdict[pinfos['name']] = [pinfos]
        to_clean = list()
        clean_count = 0
        for pname, pinfos_l in pdict.items():
            if len(pinfos_l) > 1:
                #There are some plugins to clean
                tmp_l = sorted(pinfos_l, key=lambda item: item['version'])
                to_clean += tmp_l[:-1]
                msg = "Found %s(%s). Cleaning " % (
                    pname, tmp_l[-1]['version'])
                for pinfos in to_clean:
                    clean_count += 1
                    str_info = '%s(%s)' % (pname, pinfos['version'])
                    msg += "%s, " % (str_info)
                    shutil.rmtree(pinfos['path'])
                print(msg)
        if clean_count > 0:
            print("%d plugins were uninstalled" % clean_count)
        else:
            print("Allready clean")


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

