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
         'logger': {

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
        print("CREATE_MODULE debug : ", spec)
        if spec.parent_package is not None:
            print("PARENT NAMe ;", spec.parent_package)
            parent_module = importlib.import_module(spec.parent_package)
            if hasattr(parent_module, spec.name):
                warnings.warn("Overloading an existing module attribute will \
creating %s module" % spec.name)
        else:
            parent_module = None

        res = types.ModuleType(spec.name)
        
        root_pkg_name = globals()['SITE_PACKAGE']

        res.__spec__ = spec
        res.__name__ = spec.name
        res.__loader__ = self
        res.__package__ = spec.parent_package
        res.__path__ = [] if spec._is_package else None
        if spec.site_id is not None:
            res.__site_id__ = spec.site_id
        if parent_module is not None:
            rel_name = spec.name.split('.')[-1]
            setattr(parent_module, rel_name, res)
        #sys.modules[fullname] = res
        sys.modules[spec.name] = res
        print("INFO : module %s loaded" % spec.name)
        print("INFO current state on sys.modules : ", [ mname for mname in sys.modules.keys() if mname .startswith('lodelsites.')])
        self.__dyn_module__ = res
        return res

    def load_module(self, fullname):
        if self.__dyn_module__.__name__ != fullname:
            raise MultiSiteError("The name given to load_module do not match \
the name of the handled module...")
        sys.modules[fullname] = self.__dyn_module__
        print("INFO : module %s loaded" % fullname)


##@brief Custom metapath finder that is able to handle our 
#dynamically created modules
class LodelSiteMetaPathFinder(importlib.abc.MetaPathFinder):
    
    def find_spec(fullname, path, target = None):
        print("FINDSPEC CALLEd : ", fullname, path)
        if not fullname.startswith(globals()['SITE_PACKAGE']):
            return None
        n_spl = fullname.split('.')
        site_id = n_spl[1]
        res_mod = get_site_module(site_id)
        print("Begin to walk in submodules. Starting from ", res_mod.__name__)
        print("DEBUG RESMOD : ", res_mod.__name__,  dir(res_mod))
        for nxt in n_spl[2:]:
            res_mod = getattr(res_mod, nxt)
        print("Real result : ", res_mod.__name__, res_mod)
        return res_mod.__spec__


##@brief Simple getter using site identifier
def get_site_module(identifier):
    glob_pkg = globals()['lodel_site_packages']
    if identifier not in glob_pkg:
        raise MultiSiteIdentifierError(
            "No site identified by '%s'" % identifier)
    return glob_pkg[identifier]


##@brief Create a new site module with given site identifier
#@param identifier str : site identifier
def new_site_module(identifier):
    new_module_fullname = globals()['SITE_PACKAGE'] + '.' + identifier
    new_modules = _new_site_module(
        identifier, new_module_fullname, globals()['SITE_PACKAGE_STRUCT'],
        parent = globals()['_lodel_site_root_package'])
    new_mod = new_modules[0] #fetching root module
    globals()['lodel_site_packages'][identifier] = new_mod
    setattr(globals()['_lodel_site_root_package'], identifier, new_mod)

    for mod in new_modules:
        print("Call reload on : ", mod)
        imp.reload(mod)
        for n in dir(mod):
            v = getattr(mod, n)
            if isinstance(v, types.ModuleType):
                print("\t%s : %s" % (n, getattr(mod, n)))
    return new_mod


##@brief Create a new site module (part of a site package)
#
#@note module informations are expected to be part of SITE_PACKAGE_STRUCT
#@note reccursiv function
#
#@param identifier str
#@param module_name str 
#@param module_infos dict
#@param parent : modul object
#@param all_mods list : in/out accumulator for reccursiv calls allowing to 
#return the list of all created modules
#
#@return the created module
def _new_site_module(identifier, module_name, module_infos, parent, 
        mod_acc = None):
    mod_acc = list() if mod_acc is None else mod_acc

    print("Rec debug : ", identifier, module_name, module_infos, parent)
    identifier = identifier_validation(identifier)

    if parent is None:
        parent_name = None
    else:
        parent_name = parent.__name__

    res = _module_from_spec(name = module_name, parent = parent_name,
        site_id = identifier)
    orig_modname = _original_name_from_module(res)
    if len(mod_acc) == 0:
        #we just created a site root package. Because we will reimport
        #parent modules when creating submodules we have to insert the
        #site root package NOW to the site_root_packages
        print("WARNING : inserting module as site root package : ", res)
        globals()['lodel_site_packages'][identifier] = res
    mod_acc.append(res) #Add created module to accumulator asap

    orig_mod = importlib.import_module(orig_modname)
    print("ORIG MOD = ", orig_mod)
    if 'classes' in module_infos:
        for cname in module_infos['classes']:
            orig_cls = getattr(orig_mod, cname)
            res_cls = onthefly_child_class(cname, orig_cls, parent)
            setattr(res, cname, res_cls)
    #child modules creation
    if 'modules' in module_infos:
        for mname in module_infos['modules']:
            new_mname = module_name + '.' + mname
            print("DEBUG NAME ON REC CALL : ", new_mname)
            submod = _new_site_module(
                identifier, new_mname, module_infos['modules'][mname],
                parent = res, mod_acc = mod_acc)
            submod = submod[-1]
            #setattr(res, mname, submod) #done in create_module
    return mod_acc

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
    #Creating the package that contains all site packages
    site_pkg_name = globals()['SITE_PACKAGE']
    res = _module_from_spec(name = site_pkg_name)
    globals()['_lodel_site_root_package'] = res
    sys.modules[site_pkg_name] = res
    #Add our custom metapathfinder
    sys.meta_path = [LodelSiteMetaPathFinder] + sys.meta_path
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


##@brief Replace all lodel modules references by references on dynamically
#modules
#@param mod ModuleType : the module to update
#@return the modified module
def _module_update_globals(mod):
    return None
    print("DEBUG : ", mod.__name__, dir(mod), mod.__dir__())
    site_id = mod.__site_id__
    lodel_site_package = get_site_module(mod.__site_id__)
    for kname, val in mod.__globals__:
        if isinstance(val, types.ModuleType) and \
                val.__package__.startswith('lodel'):
            #we have to replace the module reference
            fullname = "%s.%s" % (val.__package__, val.__name__)
            walkthrough = fullname.split('.')[1:]
            repl = lodel_site_package
            for submod in walkthrough:
                repl = getattr(repl, submod)
            mod.__globals__[kname] = repl
    return mod
                

##@brief Build the original fully quilified module name given a module
#@warning Behavior is totally hardcoded given the lodel2 architecture
#@param mod
#@return a fully qualified module name
def _original_name_from_module(mod):
    print("DEBUG MODNAME : ", mod, mod.__name__, mod.__package__)
    spl = mod.__name__.split('.')
    if len(spl) <= 2:
        return "lodel"
    return "lodel.%s" % ('.'.join(spl[2:]))

