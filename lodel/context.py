import importlib
import importlib.machinery
import importlib.abc
import sys
import types
import os
import re

import warnings #For the moment no way to use the logger in this file (I guess)

#A try to avoid circular dependencies problems
if 'lodel' not in sys.modules: 
    import lodel
else:
    globals()['lodel'] = sys.modules['lodel']

if 'lodelsites' not in sys.modules:
    import lodelsites
else:
    globals()['lodelsites'] = sys.modules['lodelsites']

##@brief Name of the package that will contains all the virtual lodel
#packages
CTX_PKG = "lodelsites"


#
#   Following exception classes are written here to avoid circular dependencies
#   problems.
#

##@brief Designed to be raised by the context manager
class ContextError(Exception):
    pass

##@brief Raised when an error concerning context modules occurs
class ContextModuleError(ContextError):
    pass

##@brief Designed to permit dynamic packages creation from the lodel package
#
#The class is added in first position in the sys.metapath variable. Doing this
#we override the earlier steps of the import mechanism.
#
#When called the find_spec method determine wether the imported module is
#a part of a virtual lodel package, else  it returns None and the standart
#import mechanism go further.
#If it's a submodule of a virtual lodel package we create a symlink
#to represent the lodel package os the FS and then we make python import
#files from the symlink.
#
#@note Current implementation is far from perfection. In fact no deletion
#mechanisms is written and the virtual package cannot be a subpackage of
#the lodel package for the moment...
class LodelMetaPathFinder(importlib.abc.MetaPathFinder):
    
    def find_spec(fullname, path, target = None):
        print("find_spec called : fullname=%s path=%s target=%s" % (
            fullname, path, target))
        if fullname.startswith(CTX_PKG):
            spl = fullname.split('.')
            site_identifier = spl[1]
            #creating a symlink to represent the lodel site package
            mod_path = os.path.join(lodelsites.__path__[0], site_identifier)
            if not os.path.exists(mod_path):
                os.symlink(lodel.__path__[0], mod_path, True)
            #Cache invalidation after we "created" the new package
            #importlib.invalidate_caches()
        return None


##@brief Class designed to handle context switching and virtual module
#exposure
class LodelContext(object):
    
    ##@brief FLag telling that the context handler is in single context mode
    MONOSITE = 1
    ##@brief Flag telling that the context manager is in multi context mode
    MULTISITE = 2

    ##@brief Static property storing current context name
    _current = None
    ##@brief Stores the context type (single or multiple)
    _type = None
    ##@brief Stores the contexts
    _contexts = None
    
    ##@brief Create a new context
    #@see LodelContext.new()
    def __init__(self, site_id):
        if site_id is None:
            #Monosite instanciation
            if self.__class__._type != self.__class__.MONOSITE:
                raise ContextError("Cannot instanciate a context with \
site_id set to None when we are in MULTISITE beahavior")
            else:
                #More verification can be done here (singleton specs ? )
                self.__class__._current = self.__class__._contexts = self
                self.__pkg_name = 'lodel'
                self.__package = lodel
                return
        else:
            #Multisite instanciation
            if self.__class__._type != self.__class__.MULTISITE:
                raise ContextError("Cannot instanciate a context with a \
site_id when we are in MONOSITE beahvior")
            if not self.validate_identifier(site_id):
                raise ContextError("Given context name is not a valide identifier \
    : '%s'" % site_id)
            if site_id in self.__class__._contexts:
                raise ContextError(
                    "A context named '%s' allready exists." % site_id)
            self.__id = site_id
            self.__pkg_name = '%s.%s' % (CTX_PKG, site_id)
            #Importing the site package to trigger its creation
            self.__package = importlib.import_module(self.__pkg_name)
            self.__class__._contexts[site_id] = self
    
    ##@brief Expose a module from the context
    #@param globs globals : globals where we have to expose the module
    #@param spec tuple : first item is module name, second is the alias
    def expose(self, globs, spec):
        if len(spec) != 2:
            raise ContextError("Invalid argument given. Expected a tuple of \
length == 2 but got : %s" % spec)
        module_fullname, exposure_spec = spec
        module_fullname = self._translate(module_fullname)
        if isinstance(exposure_spec, str):
            self._expose_module(globs, module_fullname, exposure_spec)
        else:
            self._expose_objects(globs, module_fullname, exposure_spec)
    
    ##@brief Utility method to expose a module with an alias name in globals
    #@param globs globals() : concerned globals dict
    #@param fullname str : module fullname
    #@param alias str : alias name
    @classmethod
    def _expose_module(cls, globs, fullname, alias):
        module = importlib.import_module(fullname)
        cls.safe_exposure(globs, module, alias)
    
    ##@brief Utility mehod to expose objects like in a from x import y,z
    #form
    #@param globs globals() : dict of globals
    #@param fullename str : module fullname
    #@param objects list : list of object names to expose
    @classmethod
    def _expose_objects(cls, globs, fullname, objects):
        errors = []
        module = importlib.import_module(fullname)
        for o_name in objects:
            if isinstance(o_name, str):
                alias = o_name
            else:
                o_name, alias = o_name
            if not hasattr(module, o_name):
                errors.append(o_name)
            else:
                cls.safe_exposure(globs, getattr(module, o_name), alias)
        if len(errors) > 0:
            msg = "Module %s does not have any of [%s] as attribute" % (
                fullname, ','.join(errors))
            raise ImportError(msg)
    
    ##@brief Translate a module fullname to the context equivalent
    #@param module_fullname str : a module fullname
    #@return The module name in the current context
    def _translate(self, module_fullname):
        if not module_fullname.startswith('lodel'):
            raise ContextModuleError("Given module is not lodel or any \
submodule : '%s'" % module_fullname)
        return module_fullname.replace('lodel', self.__pkg_name)

    ##@brief Set a context as active
    #@param site_id str : site identifier (identify a context)
    @classmethod
    def set(cls, site_id):
        if cls._type == cls.MONOSITE:
            raise ContextError("Context cannot be set in MONOSITE beahvior")
        if not cls.validate_identifier(site_id):
            raise ContextError("Given context name is not a valide identifier \
: '%s'" % site_id)
        if site_id not in cls._contexts:
            raise ContextError("No context named '%s' found." % site_id)
        cls._current = cls._contexts[site_id]
    
    ##@brief Helper method that returns the current context
    @classmethod
    def get(cls):
        if cls._current is None:
            raise ContextError("No context loaded")
        return cls._current

    ##@brief Create a new context given a context name
    #
    #@note It's just an alias to the LodelContext.__init__ method
    #@param site_id str : context name
    #@return the context instance
    @classmethod
    def new(cls, site_id):
        return cls(site_id)

    ##@brief Helper function that import and expose specified modules
    #
    #The specs given is a dict. Each element is indexed by a module
    #fullname. Items can be of two types :
    #@par Simple import with alias
    #In this case items of specs is a string representing the alias name
    #for the module we are exposing
    #@par from x import i,j,k equivalent
    #In this case items are lists of object name to expose as it in globals.
    #You can specify an alias by giving a tuple instead of a string as 
    #list element. In this case the first element of the tuple is the object
    #name and the second it's alias in the globals
    #
    #@todo make the specs format more consitant
    #@param cls : bultin params
    #@param globs dict : the globals dict of the caller module
    #@param specs dict : specs of exposure (see comments of this method)
    #@todo implements relative module imports. (maybe by looking for 
    #"calling" package in globs dict)
    @classmethod
    def expose_modules(cls, globs, specs):
        ctx = cls.get()
        for spec in specs.items():
            ctx.expose(globs, spec)
    
    ##@brief Initialize the context manager
    #
    #@note Add the LodelMetaPathFinder class to sys.metapath if type is
    #LodelContext.MULTISITE
    #@param type FLAG : takes value in LodelContext.MONOSITE or
    #LodelContext.MULTISITE
    @classmethod
    def init(cls, type=MONOSITE):
        if cls._current is not None:
            raise ContextError("Context allready started and used. Enable to \
initialize it anymore")
        if type not in ( cls.MONOSITE, cls.MULTISITE):
            raise ContextError("Invalid flag given : %s" % type)
        cls._type = type
        if cls._type == cls.MULTISITE:
            cls._contexts = dict()
            #Add custom MetaPathFinder allowing implementing custom imports
            sys.meta_path = [LodelMetaPathFinder] + sys.meta_path
        else:
            #Add a single context with no site_id
            cls._contexts = cls._current = cls(None)
    
    ##@brief Validate a context identifier
    #@param identifier str : the identifier to validate
    #@return true if the name is valide else false
    @staticmethod
    def validate_identifier(identifier):
        return identifier is None or \
            re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_]', identifier)
    
    ##@brief Safely expose a module in globals using an alias name
    #
    #@note designed to implements warning messages or stuff like that
    #when doing nasty stuff
    #
    #@todo try to use the logger module instead of warnings
    #@param globs globals : the globals where we want to expose our
    #module alias
    #@param obj object : the object we want to expose
    #@param alias str : the alias name for our module
    @staticmethod
    def safe_exposure(globs, obj, alias):
        if alias in globs:
            warnings.warn("A module exposure leads in globals overwriting for \
key '%s'" % alias)
        globs[alias] = obj
        
    ##@brief Actives a context from a path
    #@param path str : the path from which we extract a sitename
    
    def from_path(cls, path):
        site_id = path.split('/')[-1]
        if cls._type == cls.MULTISITE:
            if site_id in cls._contexts:
                cls.set(site_id)
            else
                cls._contexts[site_id] = cls.new(site_id)
        else:
            if cls._current is None:
                cls._current = cls.new()

    ##@brief Delete a site's context
    #@param site_id str : the site's name to remove the context
    def remove(cls, site_id):
        if site_id is None:
            if cls._type == cls.MULTISITE:
                raise ContextError("Cannot have a context with \
site_id set to None when we are in MULTISITE beahavior")
            del cls._contexts
        else:
            if cls._type == cls.MULTISITE:
                if site_id in cls._contexts:
                    del cls._contexts[site_id]
                else:
                    raise ContextError("No site %s exist" % site_id)
            else:
                raise ContextError("Cannot have a context with \
    site_id set when we are in MONOSITE beahavior")
        

