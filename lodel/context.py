import importlib
import importlib.machinery
import importlib.abc
import sys
import types
import os
import os.path
import re
import copy

import warnings #For the moment no way to use the logger in this file (I guess)

#A try to avoid circular dependencies problems
if 'lodel' not in sys.modules: 
    import lodel
else:
    globals()['lodel'] = sys.modules['lodel']

if 'lodelsites' in sys.modules:
    #This should be true since LodelContext init method is called
    #for a MULTISITE context handling
    globals()['lodelsites'] = sys.modules['lodelsites']

from lodel import buildconf

##@brief Name of the package that will contains all the virtual lodel
#packages
CTX_PKG = "lodelsites"

##@brief Reserved context name for loading steps
#@note This context is designed to be set at loading time, allowing lodel2
#main process to use lodel packages
LOAD_CTX = "__loader__"


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

def dir_for_context(site_identifier):
    _, ctx_path = LodelContext.lodelsites_paths()
    return os.path.join(ctx_path, site_identifier)
    

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
#
#@note Current implementation is far from perfection. In fact no deletion
#mechanisms is written and the virtual package cannot be a subpackage of
#the lodel package for the moment...
#@note Current implementation asserts that all plugins are in CWD
#a symlink will be done to create a copy of the plugins folder in 
#lodelsites/SITENAME/ folder
class LodelMetaPathFinder(importlib.abc.MetaPathFinder):
    
    ##@brief implements the find_spec method of MetaPathFinder
    #
    #@param fullname str : module fullname
    #@param path str : with be the value of __path__ of the parent package
    #@param target module : is a module object that the finder may use to
    #make a more educated guess about what spec to return
    #@see https://docs.python.org/3/library/importlib.html#importlib.abc.MetaPathFinder
    def find_spec(fullname, path, target = None):
        if fullname.startswith(CTX_PKG+'.'):
            spl = fullname.split('.')
            site_identifier = spl[1]
            #creating a symlink to represent the lodel site package
            mod_path = dir_for_context(site_identifier)
            if not os.path.exists(mod_path):
                os.symlink(lodel.__path__[0], mod_path, True)
            #Cache invalidation after we "created" the new package
            #importlib.invalidate_caches()
        return None
    #def invalidate_caches(): pass


##@brief Class designed to handle context switching and virtual module
#exposure
#
#The main entrypoint of this class is the expose_module method. A kind of
#equivalent of the various import X [as Y], from X import Y [as Z] etc.
#existing in Python.
#The expose_module method add a preffix to the module fullname in order
#to make it reconizable by the LodelMetaPathfinder::find_spec() method.
#All module names are translated before import. The preffix is set at
#__init__ call in __pkg_name. The resulting name is __pkg_name + fullname
#
#@par examples 
#When asking for lodel.leapi.leobject :
#- in MONOSITE resulting module will be lodel.leapi.leobject
#- in MULTISITE resulting module name will be 
#lodelsites.SITE_ID.lodel.leapi.leobject
#
#The lodelsites package will be a subdir of buildconf.MULTISITE_CONTEXTDIR
#that will be itself added to sys.path in order to be able to import
#lodelsites
#
#@par Notes about dyncode exposure
#In MULTISITE mode the dyncode will be stored as a python module in 
#buildconf.MULTISITE_CONTEXTDIR/SITE_ID/leapi_dyncode.py . The dyncode
#exposale process in MULTISITE mode is simply done by asking LodelContext
#to expose a module named leapi_dyncode. The LodelContext::_translate()
#method is able to produce a correct name for this module.
#In MONOSITE mode the dyncode will be stored as a python module in 
#the site directory. In this case the _translate method will do the same
#transformation than for the others modules. But in MONOSITE mode the 
#module preffix is empty. Resulting in import leapi_dyncode. This will
#work asserting that cwd in MONOSITE mode is the instance directory.
#
#
#
#@note a dedicated context named LOAD_CTX is used as context for the 
#loading process
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

    ##@brief Flag indicating if the classe is initialized
    __initialized = False

    ##@brief Stores path used by MULTISITE instance
    #
    #This variable is a tuple with 2 elements (in this order):
    #- lodelsites datadir (ex: /var/lodel2/MULTISITE_NAME/datadir/)
    #- lodelsites contextdir (ex: /varL/lodel2/MULTISITE_NAME/.ctx/lodelsites)
    __lodelsites_paths = None

    ##@brief Create a new context
    #@see LodelContext.new()
    def __init__(self, site_id, instance_path = None):
        if site_id is None and self.multisite():
            site_id = LOAD_CTX
        if self.multisite() and site_id is not LOAD_CTX:
            with LodelContext.with_context(None) as ctx:
                ctx.expose_modules(globals(), {'lodel.logger': 'logger'})
                logger.info("New context instanciation named '%s'" % site_id)
        if site_id is None:
            self.__id = "MONOSITE"
            #Monosite instanciation
            if self.multisite():
                raise ContextError("Cannot instanciate a context with \
site_id set to None when we are in MULTISITE beahavior")
            else:
                #More verification can be done here (singleton specs ? )
                self.__class__._current = self.__class__._contexts = self
                self.__pkg_name = 'lodel'
                self.__package = lodel
                self.__instance_path = os.getcwd()
                return
        else:
            #Multisite instanciation
            if not self.multisite():
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

            if instance_path is None:
                """
                raise ContextError("Cannot create a context without an \
instance path")
                """
                warnings.warn("It can be a really BAD idea to create a \
a context without a path......")
                self.__instance_path = None
            else:
                self.__instance_path = os.path.realpath(instance_path)
            #Importing the site package to trigger its creation
            self.__package = importlib.import_module(
                self.__pkg_name)
            self.__class__._contexts[site_id] = self
        #Designed to be use by with statement
        self.__previous_ctx = None

    def __repr__(self):
        return '<LodelContext name="%s">' % self.__id
    
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

    ##@brief Return a module from current context
    def get_module(self, fullname):
        fullname = self._translate(fullname)
        module = importlib.import_module(fullname)
        return module
        
    
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
    
    ##@return identifier for current context
    @classmethod
    def current_id(cls):
        return cls._current.__id

    ##@return True if the class is in MULTISITE mode
    @classmethod
    def multisite(cls):
        return cls._type == cls.MULTISITE
    
    ##@brief helper class to use LodeContext with with statement
    #@note alias to get method
    #@note maybe useless
    #@todo delete me
    @classmethod
    def with_context(cls, target_ctx_id):
        return cls.get(target_ctx_id)

    ##@brief Set a context as active
    #
    #This method handle the context switching operations. Some static 
    #attributes are set at this step.
    #@note if not in LOAD_CTX a sys.path update is done
    #@warning Inconsistency with lodelsites_datasource, we build again the
    #site context dir path using site_id. This information should come
    #from only one source
    #@param site_id str : site identifier (identify a context)
    #@todo unify the generation of the site specific context dir path
    @classmethod
    def set(cls, site_id):
        if cls._type == cls.MONOSITE:
            raise ContextError("Context cannot be set in MONOSITE beahvior")

        site_id = LOAD_CTX if site_id is None else site_id
        if not cls.validate_identifier(site_id):
            raise ContextError("Given context name is not a valide identifier \
: '%s'" % site_id)
        if site_id not in cls._contexts:
            raise ContextError("No context named '%s' found." % site_id)
        if cls.current_id() != LOAD_CTX and site_id != LOAD_CTX:
            raise ContextError("Not allowed to switch into a site context \
from another site context. You have to switch back to LOAD_CTX before")
        wanted_ctx = cls._contexts[site_id]
        if hasattr(wanted_ctx, '__instance_path'):
            os.chdir(self.__instance_path) #May cause problems and may be obsolete
        cls._current = wanted_ctx
        return cls._current
    
    ##@brief Getter for contexts
    #@param ctx_id str | None | False : if False return the current context
    #@return A LodelContext instance
    @classmethod
    def get(cls, ctx_id = False):
        if ctx_id is False:
            if cls._current is None:
                raise ContextError("No context loaded")
            return cls._current
        ctx_id = LOAD_CTX if ctx_id is None else ctx_id
        if ctx_id not in cls._contexts:
            raise ContextError("No context identified by '%s'" % ctx_id)
        return cls._contexts[ctx_id]
    
    ##@brief Returns the name of the loaded context
    @classmethod
    def get_name(cls):
        if cls._current is None:
            raise ContextError("No context loaded")
        return copy.copy(cls._current.__id)
        

    ##@brief Create a new context given a context name and switch in it
    #
    #@note It's just an alias to the LodelContext.__init__ method
    #@param site_id str : context name
    #@return the context instance
    @classmethod
    def new(cls, site_id, instance_path = None):
        if site_id is None:
            site_id = LOAD_CTX
        return cls(site_id, instance_path)

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
    
    ##@brief Return a module from current context
    #@param fullname str : module fullname
    #@todo check if not globals are set when getting a module ! (if so
    #checks all calls to this method to check that this assertion was not 
    #made)
    @classmethod
    def module(cls, fullname):
        return cls.get().get_module(fullname)
        
    ##@brief Expose leapi_dyncode module
    @classmethod
    def expose_dyncode(cls, globs, alias = 'leapi_dyncode'):
        cls.get().expose_modules(globs, { 'leapi_dyncode': alias })

    ##@brief Initialize the context manager
    #
    #@note Add the LodelMetaPathFinder class to sys.metapath if type is
    #LodelContext.MULTISITE
    #@note lodelsites package name is hardcoded and has to be
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
            #Woot hardcoded stuff with no idea of what it implies :-P
            lodelsites_path = os.getcwd() #Same assert in the loader
            cls.__lodelsites_paths = (
                os.path.join(lodelsites_path, buildconf.MULTISITE_DATADIR),
                os.path.join(lodelsites_path,
                    buildconf.MULTISITE_CONTEXTDIR))
            #Now we are able to import lodelsites package
            sys.path.append(os.path.dirname(cls.__lodelsites_paths[1]))
            if 'lodelsites' not in sys.modules:
                import lodelsites
            globals()['lodelsites'] = sys.modules['lodelsites']
            #End of Woot
            cls._contexts = dict()
            #Add custom MetaPathFinder allowing implementing custom imports
            sys.meta_path = [LodelMetaPathFinder] + sys.meta_path
            #Create and set __loader__ context
            ctx = cls.new(LOAD_CTX)
            #DIRTY enforcing
            cls._current = ctx
            cls.set(LOAD_CTX)
        else:
            #Add a single context with no site_id
            cls._contexts = cls._current = cls(None)
        cls.__initialized = True
    
    ##@return True if the class is initialized
    @classmethod
    def is_initialized(cls):
        return cls.__initialized
    
    ##@brief Return the directory of the package of the current loaded context
    @classmethod
    def context_dir(cls):
        if cls._type == cls.MONOSITE:
            return './'
        return os.path.join(cls.__lodelsites_paths[1],
            cls._current.__id)
        

    ##@brief Validate a context identifier
    #@param identifier str : the identifier to validate
    #@return true if the name is valide else false
    @staticmethod
    def validate_identifier(identifier):
        if identifier == LOAD_CTX:
            return True
        return identifier is None or \
            re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_]', identifier)
    
    ##@brief Safely expose a module in globals using an alias name
    #
    #@note designed to implements warning messages or stuff like that
    #when doing nasty stuff
    #
    #@warning Logging stuffs may lead in a performance issue
    #
    #@todo try to use the logger module instead of warnings
    #@param globs globals : the globals where we want to expose our
    #module alias
    #@param obj object : the object we want to expose
    #@param alias str : the alias name for our module
    @staticmethod
    def safe_exposure(globs, obj, alias):
        if alias in globs:
            if globs[alias] != obj:
                print("Context '%s' : A module exposure leads in globals overwriting for \
key '%s' with a different value : %s != %s" % (LodelContext.get_name(), alias, globs[alias], obj))
                """#Uncomment this bloc to display a stack trace for dangerous modules overwriting
                print("DEBUG INFOS : ")
                import traceback
                traceback.print_stack()
                """
            else:
                print("Context '%s' : A module exposure leads in a useless replacement for \
key '%s'" % (LodelContext.get_name(),alias))
        globs[alias] = obj
        
    ##@brief Create a context from a path and returns the context name
    #@param path str : the path from which we extract a sitename
    #@return the site identifier
    @classmethod
    def from_path(cls, path):
        if cls._type != cls.MULTISITE:
            raise ContextError("Cannot create a context from a path in \
MONOSITE mode")
        site_id = os.path.basename(path.strip('/'))
        path = os.path.realpath(path)
        if not cls.validate_identifier(site_id):
            raise ContextError(
                "Unable to create a context named '%s'" % site_id)
        cls.new(site_id, path)
        return site_id
    
    ##@brief Return a tuple containing lodelsites datadir & contextdir (
    #in this order)
    @classmethod
    def lodelsites_paths(cls):
        if cls.__lodelsites_paths is None:
            raise ContextError('No paths available')
        return copy.copy(cls.__lodelsites_paths)

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
    #
    #Two transformation are possible :
    #- we are importing a submodule of the lodel package : resulting module
    #name will be : self.__pkg_name + module_fullname
    #- we are importing the dyncode : resulting module name is :
    #self.__pkg_name + dyncode_modulename
    #@param module_fullname str : a module fullname
    #@return The module name in the current context
    def _translate(self, module_fullname):
        if module_fullname.startswith('lodel'):
            return self.__pkg_name + module_fullname[5:]
        if module_fullname.startswith('leapi_dyncode'):
            return self.__pkg_name+'.'+module_fullname
        raise ContextModuleError("Given module is not lodel nor dyncode \
or any submodule : '%s'" % module_fullname)

    ##@brief Implements the with statement behavior
    #@see https://www.python.org/dev/peps/pep-0343/
    #@see https://wiki.python.org/moin/WithStatement
    def __enter__(self):
        if not self.multisite:
            warnings.warn("Using LodelContext with with statement in \
MONOSITE mode")
        if self.__previous_ctx is not None:
            raise ContextError("__enter__ called but a previous context \
is allready registered !!! Bailout")
        current = LodelContext.get().__id
        if current != self.__id:
            #Only switch if necessary
            self.__previous_ctx = LodelContext.get().__id
            LodelContext.set(self.__id)
        return self

    ##@brief Implements the with statement behavior
    #@see https://www.python.org/dev/peps/pep-0343/
    #@see https://wiki.python.org/moin/WithStatement
    def __exit__(self, exc_type, exc_val, exc_tb):
        prev = self.__previous_ctx
        self.__previous_ctx = None
        if prev is not None:
            #Only restore if needed
            LodelContext.set(self.__previous_ctx)

