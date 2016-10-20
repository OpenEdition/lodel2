import types
import sys
import imp
import importlib.machinery, importlib.abc

import re
import warnings

from .exceptions import MultiSiteIdentifierError

##@brief Constant name of the package containing all sites module
SITE_PACKAGE = 'lodelsites'
##@brief Stores all the lodel sites modules indexed by site identifier
lodel_site_packages = dict()
##@brief Will stores the module object of the SITE_PACKAGE
_lodel_site_root_package = None
##@brief Stores the site identifier validation re
_site_identifier_re = None


SITE_PACKAGE_STRUCT = {
    'modules': {
        'auth': {

         },
         'settings': {

         },
         'plugin': {
            'modules': {
                'hooks': {
                    'classes': [ 'DecoratedWrapper', 'LodelHook' ]
                },
                'plugins': {
                    'classes': [
                        'PluginVersion', 'MetaPlugType', 'Plugin',
                        'CustomMethod']
                },
                'interface': {
                    'classes': [ 'InterfacePlugin']
                },
                'extensions': {
                    'classes': [ 'Extension']
                }
            },
         }
    },
    'classes': {}
}

class LodelSiteModuleSpec(importlib.machinery.ModuleSpec):
    
    ##@brief Add a site_id attribute to ModuleSpec object
    #
    #@param name str : fully qualified module name
    #@param loader : module loader. Child of importlib.abc.Loader and in our
    #case mostly CustomModuleLoader instances
    #@param parent str : parent absolute package name. Will be used to set
    #new module __package___ attribute
    #@param origin None : None because no source code
    #@param loader_state ? <- leave None
    #@param is_package bool : <- useless, can be deleted
    #
    #@see https://docs.python.org/3.4/library/importlib.html#importlib.machinery.ModuleSpec
    def __init__(self, name, loader, *,
            parent=None, origin=None, loader_state=None, is_package=None,
            site_id = None):
        super().__init__(name=name, loader=loader, origin=origin, 
            loader_state = loader_state)
        ##@brief Stores the parent package fullname
        self.parent_package = parent
        ##@brief Stores the module site_id
        self.site_id = None
        self._is_package = False if is_package is None else True
        if not site_id is None:
            self.site_id = site_id

    def __str__(self):
        res = super().__str__()
        res = res[:-1] +", site_id = %s, parent = %s)" % (
            self.site_id, repr(self.parent))
        return res


##@brief Custom class of module Loader
#
#Designed to handle dynamic module creation for lodel2 sites
#@see https://docs.python.org/3.4/library/importlib.html#importlib.abc.Loader
#@see https://docs.python.org/3.4/library/types.html#types.ModuleType
class LodelSiteModuleLoader(importlib.abc.Loader):
    
    ##@brief Handles module creation
    #@param spec ModuleSpec instance
    #@return The newly created module
    def create_module(self, spec):
        #Here we do not want to import but get the module object of the parent
        #to store it's reference and set the new module as attribute
        if spec.parent_package is not None:
            parent_module = importlib.import_module(spec.parent_package)
            if hasattr(parent_module, spec.name):
                warnings.warn("Overloading an existing module attribute will \
creating %s module" % spec.name)
        else:
            parent_module = None

        res = types.ModuleType(spec.name)
        res.__name__ = spec.name
        res.__loader__ = self
        res.__package__ = spec.parent_package
        res.__path__ = [] if spec._is_package else None
        if spec.site_id is not None:
            res.__site_id__ = spec.site_id
        if parent_module is not None:
            setattr(parent_module, spec.name, res)
        if res.__package__ is not None:
            fullname = "%s.%s" % (res.__package__, res.__name__)
        else:
            fullname = res.__name__
        sys.modules[fullname] = res
        return res

        


##@brief Create a new site module with given site identifier
#@param identifier str : site identifier
def new_site_module(identifier):
    new_mod = _new_site_module(
        identifier, identifier, globals()['SITE_PACKAGE_STRUCT'],
        parent = globals()['_lodel_site_root_package'])
    globals()['lodel_site_packages']['identifier'] = new_mod
    setattr(globals()['_lodel_site_root_package'], identifier, new_mod)
    return new_mod

def get_site_module(identifier):
    glob_pkg = globals()['lodel_site_packages']
    if identifier not in glob_pkg:
        raise 

##@brief Create a new site module (part of a site package)
#
#@note module informations are expected to be part of SITE_PACKAGE_STRUCT
#@note reccursiv function
#
#@param identifier str
#@param module_name str 
#@param module_infos dict
#@param parent : modul object
#
#@return the created module
def _new_site_module(identifier, module_name, module_infos, parent):
    print("Rec debug : ", identifier, module_name, module_infos, parent)
    identifier = identifier_validation(identifier)
    orig_modname = _original_name_from_module(parent)
    if parent.__name__ != globals()['SITE_PACKAGE']:
        orig_modname += '.'+module_name
    if parent.__package__ is None:
        parent_fullname = parent.__name__
    else:
        parent_fullname = "%s.%s" % (parent.__package__, parent.__name__)
    res = _module_from_spec(name = module_name, parent = parent_fullname,
        site_id = identifier)
    orig_mod = importlib.import_module(orig_modname)
    if 'classes' in module_infos:
        for cname in module_infos['classes']:
            orig_cls = getattr(orig_mod, cname)
            res_cls = onthefly_child_class(cname, orig_cls, parent)
            setattr(res, cname, res_cls)
    #child modules creation
    if 'modules' in module_infos:
        for mname in module_infos['modules']:
            submod = _new_site_module(
                identifier, mname, module_infos['modules'][mname],
                parent = res)
            setattr(res, mname, submod)
    return res

##@brief Validate a site identifier
#@param identifier str
#@return the identifier
#@throw MultiSiteIdentifierError on invalid id
def identifier_validation(identifier):
    re_str = r'^[a-zA-Z][a-zA-Z0-9-]*$'
    _site_identifier_re = globals()['_site_identifier_re']
    if _site_identifier_re is None:
        _site_identifier_re = re.compile(re_str)
        globals()['_site_identifier_re'] = _site_identifier_re
    if not _site_identifier_re.match(identifier):
        raise MultiSiteIdentifierError("Excpected an identifier that matches \
r'%s', but got '%s'" % (re_str, identifier))
    return identifier


##@brief Create new root package for a lodel site
#@param identifer str : the site identifier
def new_site_root_package(identifier):
    identifier_validation(identifier)
    if identifier in _lodel_site_root_package:
        raise NameError("A site identified by '%s' allready exists")
    module_name = identifier
    res = _module_from_spec(
        name = identifier, parent = globals()['SITE_PACKAGE'])
    _lodel_site_root_packages[identifier] = res
    return res

##@brief Create a new child class on the fly
#@param identifier str : site identifier
#@param original_cls class : the original class (will be the single base class
#of our dynamically created class)
#@param parent_module module object : the module designed to contains the class
#@return the created class
def onthefly_child_class(identifier, original_cls, parent_module):
    def ns_callback(ns):
        ns['__module__'] = parent_module.__name__
        ns['__site_id__'] = identifier
    res = types.new_class(original_cls.__name__, (original_cls,), None,
        ns_callback)
    setattr(parent_module, original_cls.__name__, res)
    return res

##@brief Module initialisation function
#
#Takes care to create the lodel_site_package module object
def init_module():
    site_pkg_name = globals()['SITE_PACKAGE']
    res = _module_from_spec(name = site_pkg_name)
    globals()['_lodel_site_root_package'] = res
    sys.modules[site_pkg_name] = res
    return res
    

##@brief Utility function that takes LodelSiteModuleSpec __init__ arguments
#as parameter and handles the module creation
#@return A newly created module according to given arguments
def _module_from_spec(name, parent = None, origin = None, loader_state = None,
        is_package = None, site_id = None):
    loader = LodelSiteModuleLoader()
    spec = LodelSiteModuleSpec(name = name, parent = parent, origin = origin,
        loader_state = None, loader = loader, is_package = is_package,
        site_id = site_id)
    
    return loader.create_module(spec)


##@brief Build the original fully quilified module name given a module
#@warning Behavior is totally hardcoded given the lodel2 architecture
#@param mod
#@return a fully qualified module name
def _original_name_from_module(mod):
    print("DEBUG MODNAME : ", mod, mod.__name__, mod.__package__)
    if mod.__name__ == globals()['SITE_PACKAGE'] or mod.__package__ is None:
        return 'lodel'
    res = "%s.%s" % (mod.__package__, mod.__name__)
    spl = res.split('.')
    if len(spl) <= 2:
        return 'lodel'
    res = "lodel."+ ('.'.join(spl[2:]))
    return res

