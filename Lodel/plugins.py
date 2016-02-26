#-*- coding: utf-8 -*-

import inspect
import os, os.path
import warnings

from Lodel.settings import Settings
from Lodel import logger
from Lodel.hooks import LodelHook
from Lodel.user import authentication_method, identification_method

## @brief Handle registration and fetch of plugins functions that will be bound to LeCrud subclass
#
# @note This class exists because of strange behavior with decorator's class inheritance (static attributes was modified by child class)
class LeapiPluginsMethods(object):

    ## @brief Stores instance methods we want to bind to LeCrud subclass instances
    __methods = {}
    ## @brief Stores classmethods we want to bind to LeCrud subclass
    __classmethods = {}
    
    ## @brief Register a new method for LeApi enhancement
    # @param class_method bool : if True register a classmethod
    # @param leapi_classname str : the classname
    # @param method callable : the method to bind
    # @param bind_name str|None : binding name, if None use the decorated function name
    @classmethod
    def register(cls, class_method, leapi_classname, method, bind_name = None):
        if bind_name is None:
            bind_name = method.__name__ # use method name if no bind_name specified

        methods = cls.__classmethods if class_method else cls.__methods

        if leapi_classname not in methods:
            methods[leapi_classname] = dict()
        elif bind_name in methods[leapi_classname]:
            orig_fun = methods[leapi_classname][bind_name]
            msg = 'Method overwriting : %s.%s will be registered as %s for %s in place of %s.%s' % (
                inspect.getmodule(orig_fun).__name__,
                orig_fun.__name__,
                bind_name,
                leapi_classname,
                inspect.getmodule(method).__name__,
                method.__name__
            )
            logger.warning(msg)
        methods[leapi_classname][bind_name] = method
        # I was thinking that dict are refrerences...
        if class_method:
            cls.__classmethods = methods
        else:
            cls.__methods = methods
    
    ## @brief Fetch all methods that has to be bound to a class
    # @param class_method bool : if true returns classmethods
    # @param call_cls LeCrud subclass : the targeted class
    # @return a dict with wanted bind name as key and callable as value
    @classmethod
    def get_methods(cls, class_method, call_cls):
        methods = cls.__classmethods if class_method else cls.__methods
        result = dict()
        for leapi_classname in methods:
            leapi_cls = call_cls.name2class(leapi_classname)
            # Strange tests are made on call_cls.__name__ because the name2class method
            # is not working when called from LeObject at init time...
            if leapi_cls is False and leapi_classname != call_cls.__name__:
                logger.warning("Unable to find leapi class %s" % (leapi_classname))
            elif leapi_classname == call_cls.__name__ or issubclass(call_cls, leapi_cls):
                result.update(methods[leapi_classname])
        return result


## @brief Decorator class for leapi object enhancement
#
# This decorator allows plugins to bind methods to leapi
# classes.
#
# The decorator take 2 arguments :
# - leapi_cls_name str : the leapi class name
# - method_name str (optional) : the method name once bind (if None the decorated function name will be used)
#
# @note there is another optionnal argument class_method (a bool), but you should not use it and use the leapi_classmethod decorator instead
class leapi_method(object):
    ## @brief Constructor for plugins leapi enhancement methods
    # @param leapi_cls_name str : the classname we want to bind a method to
    # @param method_name str|None : binding name, if None use the decorated function name
    def __init__(self, leapi_cls_name, method_name = None, class_method = False):
        self.__leapi_cls_name = leapi_cls_name
        self.__method_name = method_name
        self.__method = None
        self.__class_method = bool(class_method)
    
    ## @brief Called at decoration time
    # @param method callable : the decorated function
    def __call__(self, method):
        self.__method = method
        if self.__method_name is None:
            self.__method_name = method.__name__
        self.__register()
    
    ## @biref Register a method to the method we want to bind
    def __register(self):
        LeapiPluginsMethods.register(self.__class_method, self.__leapi_cls_name, self.__method, self.__method_name)


## @brief Same behavior thant leapi_method but registers classmethods
class leapi_classmethod(leapi_method):
    def __init__(self, leapi_cls_name, method_name = None):
        super().__init__(leapi_cls_name, method_name, True)
    

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
