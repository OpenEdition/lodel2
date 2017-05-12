import pkgutil
import os
from lodel.editorial_model.model import EditorialModel
from lodel.leapi import lefactory
LODEL_COMMANDS_PATH = os.path.join(__package__, "commands")


def register_commands(manager):
    for _, modulename, _ in pkgutil.iter_modules([LODEL_COMMANDS_PATH]):
        command_module = __import__("%s.%s" % (LODEL_COMMANDS_PATH.replace("/","."),modulename), fromlist=['LodelCommand'])
        manager.add_command(modulename, getattr(command_module, 'LodelCommand')())

##
# @todo move this method in the corresponding module and change its calls in the corresponding commands
def generate_dyncode(model_file, translator):
    model = EditorialModel.load(translator, filename=model_file)
    dyncode = lefactory.dyncode_from_em(model)
    return dyncode

def init_all_datasources(dyncode):
    from lodel.plugin.datasource_plugin import DatasourcePlugin
    from lodel import logger

    ds_cls = dict() # EmClass indexed by rw_datasource
    for cls in dyncode.dynclasses:
        ds = cls._datasource_name
        if ds not in ds_cls:
            ds_cls[ds] = [cls]
        else:
            ds_cls[ds].append(cls)
    
    for ds_name in ds_cls:
        mh = DatasourcePlugin.init_migration_handler(ds_name)
        #Retrieve plugin_name & ds_identifier for logging purpose
        plugin_name, ds_identifier = DatasourcePlugin.plugin_name(
            ds_name, False)
        try:
            mh.init_db(ds_cls[ds_name])
        except Exception as e:
            msg = "Migration failed for datasource %s(%s.%s) when running \
init_db method: %s"
            msg %= (ds_name, plugin_name, ds_identifier, e)
        logger.info("Database initialisation done for %s(%s.%s)" % (
            ds_name, plugin_name, ds_identifier))

def list_registered_hooks():
    from lodel.plugin.hooks import LodelHook
    from lodel.plugin.plugins import Plugin
    
    Plugin.load_all()
    hlist = LodelHook.hook_list()
    print("Registered hooks are : ")
    for name in sorted(hlist.keys()):
        print("\t- %s is registered by : " % name)
        for reg_hook in hlist[name]:
            hook, priority = reg_hook
            msg = "\t\t- {modname}.{funname} with priority : {priority}"
            msg = msg.format(
                modname = hook.__module__,
                funname = hook.__name__,
                priority = priority)
            print(msg)
        print("\n")

##@brief update plugin's discover cache
def update_plugin_discover_cache(path_list = None):
    os.environ['LODEL2_NO_SETTINGS_LOAD'] = 'True'
    from lodel.plugin.plugins import Plugin
    res = Plugin.discover(path_list)
    print("Plugin discover result in %s :\n" % res['path_list'])
    for pname, pinfos in res['plugins'].items():
        print("\t- %s %s -> %s" % (
            pname, pinfos['version'], pinfos['path']))
