#-*- coding: utf-8 -*-

import inspect
import os, os.path
import warnings

from Lodel.settings import Settings
from Lodel.hooks import LodelHook
from Lodel.user import authentication_method, identification_method


## @brief Returns a list of human readable registered hooks
# @param names list | None : optionnal filter on name
# @param plugins list | None : optionnal filter on plugin name
# @return A str representing registered hooks
def list_hooks(names = None, plugins = None):
    res = ""
    # Hooks registered and handled by Lodel.usera
    for decorator in [authentication_method, identification_method]:
        if names is None or decorator.__name__ in names:
            res += "%s :\n" % decorator.__name__
            for hook in decorator.list_methods():
                module = inspect.getmodule(hook).__name__
                if plugins is not None: # Filter by plugin
                    spl = module.split('.')
                    if spl[-1] not in plugins:
                        continue
                res += "\t- %s.%s\n" % (module, hook.__name__)
    # Hooks registered and handled by Lodel.hooks
    registered_hooks = LodelHook.hook_list(names)
    for hook_name, hooks in registered_hooks.items():
        if names is None or hook_name in names:
            res += "%s :\n" % hook_name
            for hook, priority in hooks:
                module = inspect.getmodule(hook).__name__
                if plugins is not None: # Filter by plugin
                    spl = module.split('.')
                    if spl[-1] not in plugins:
                        continue
                res += "\t- %s.%s ( priority %d )\n" % (module, hook.__name__, priority)
    return res

## @brief Return a human readable list of plugins
# @param activated bool | None : Optionnal filter on activated or not plugin
# @return a str
def list_plugins(activated = None):
    res = ""
    # Activated plugins
    if activated is None or activated:
        res += "Activated plugins :\n"
        for plugin_name in Settings.plugins:
            res += "\t- %s\n" % plugin_name
    # Deactivated plugins
    if activated is None or not activated:
        plugin_dir = os.path.join(Settings.lodel2_lib_path, 'plugins')
        res += "Not activated plugins :\n"
        all_plugins = [fname for fname in os.listdir(plugin_dir) if fname != '.' and fname != '..' and fname != '__init__.py']
        for plugin_name in all_plugins:
            if os.path.isfile(os.path.join(plugin_dir, plugin_name)) and plugin_name.endswith('.py'):
                plugin_name = ''.join(plugin_name.split('.')[:-1])
            elif not os.path.isdir(os.path.join(plugin_dir, plugin_name)):
                warnings.warn("Dropped file in plugins directory : '%s'" % (os.path.join(plugin_dir, plugin_name)))
                continue
            elif plugin_name == '__pycache__':
                continue

            if plugin_name not in Settings.plugins:
                res += "\t- %s\n" % plugin_name
    return res

## @brief Utility function that generate the __all__ list of the plugins/__init__.py file
# @return A list of module name to import
def _all_plugins():
    plugin_dir = os.path.join(Settings.lodel2_lib_path, 'plugins')
    res = list()
    for plugin_name in Settings.plugins:
        if os.path.isdir(os.path.join(plugin_dir, plugin_name)):
            # plugin is a module
            res.append('%s' % plugin_name)
            #res.append('%s.loader' % plugin_name)
        elif os.path.isfile(os.path.join(plugin_dir, '%s.py' % plugin_name)):
            # plugin is a simple python sourcefile
            res.append('%s' % plugin_name)
    return res
            
            
    
