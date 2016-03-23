#-*- coding: utf-8 -*-

import itertools
import warnings
import copy
import hashlib

from lodel.utils.mlstring import MlString

from lodel.editorial_model.exceptions import *

## @brief Abstract class to represent editorial model components
# @see EmClass EmField
class EmComponent(object):
    
    ## @brief Instanciate an EmComponent
    # @param uid str : uniq identifier
    # @param display_name MlString|str|dict : component display_name
    # @param help_text MlString|str|dict : help_text
    def __init__(self, uid, display_name = None, help_text = None, group = None):
        if self.__class__ == EmComponent:
            raise NotImplementedError('EmComponent is an abstract class')
        self.uid = uid
        self.display_name = None if display_name is None else MlString(display_name)
        self.help_text = None if help_text is None else MlString(help_text)
        self.group = group
    
    def __str__(self):
        if self.display_name is None:
            return str(self.uid)
        return str(self.display_name)

    def d_hash(self):
        m = hashlib.md5()
        for data in (
                        self.uid,
                        'NODISPNAME' if self.display_name is None else str(self.display_name.d_hash()),
                        'NOHELP' if self.help_text is None else str(self.help_text.d_hash()),
                        'NOGROUP' if self.group is None else str(self.group.d_hash()),
        ):
            m.update(bytes(data, 'utf-8'))
        return int.from_bytes(m.digest(), byteorder='big')


## @brief Handles editorial model objects classes
#
# @note The inheritance system allow child classes to overwrite parents EmField. But it's maybe not a good idea
class EmClass(EmComponent):
    
    ## @brief Instanciate a new EmClass
    # @param uid str : uniq identifier
    # @param display_name MlString|str|dict : component display_name
    # @param abstract bool : set the class as asbtract if True
    # @param parents list: parent EmClass list or uid list
    # @param help_text MlString|str|dict : help_text
    def __init__(self, uid, display_name = None, help_text = None, abstract = False, parents = None, group = None):
        super().__init__(uid, display_name, help_text, group)
        self.abstract = bool(abstract)
        if parents is not None:
            if not isinstance(parents, list):
                parents = [parents]
            for parent in parents:
                if not isinstance(parent, EmClass):
                    raise ValueError("<class EmClass> expected in parents list, but %s found" % type(parent))
        else:
            parents = list()
        self.parents = parents
        ## @brief Stores EmFields instances indexed by field uid
        self.__fields = dict() 
    
    ## @brief Property that represent a dict of all fields (the EmField defined in this class and all its parents)
    @property
    def __all_fields(self):
        res = dict()
        for pfields in [ p.__all_fields for p in self.parents]:
            res.update(pfields)
        res.update(self.__fields)
        return res

    ## @brief EmField getter
    # @param uid None | str : If None returns an iterator on EmField instances else return an EmField instance
    # @param no_parents bool : If True returns only fields defined is this class and not the one defined in parents classes
    # @return A list on EmFields instances (if uid is None) else return an EmField instance
    def fields(self, uid = None, no_parents = False):
        fields = self.__fields if no_parents else self.__all_fields
        try:
            return list(fields.values()) if uid is None else fields[uid]
        except KeyError:
            raise EditorialModelError("No such EmField '%s'" % uid)

    ## @brief Add a field to the EmClass
    # @param emfield EmField : an EmField instance
    # @warning do not add an EmField allready in another class !
    # @throw EditorialModelException if an EmField with same uid allready in this EmClass (overwritting allowed from parents)
    def add_field(self, emfield):
        if emfield.uid in self.__fields:
            raise EditorialModelException("Duplicated uid '%s' for EmField in this class ( %s )" % (emfield.uid, self))
        self.__fields[emfield.uid] = emfield
        emfield._emclass = self
        return emfield
    
    ## @brief Create a new EmField and add it to the EmClass
    # @param uid str : the EmField uniq id
    # @param **field_kwargs :  EmField constructor parameters ( see @ref EmField.__init__() ) 
    def new_field(self, uid, **field_kwargs):
        return self.add_field(EmField(uid, **field_kwargs))

    def d_hash(self):
        m = hashlib.md5()
        payload = str(super().d_hash()) + ("1" if self.abstract else "0")
        for p in sorted(self.parents):
            payload += str(p.d_hash())
        m.update(bytes(payload, 'utf-8'))
        return int.from_bytes(m.digest(), byteorder='big')


## @brief Handles editorial model classes fields
class EmField(EmComponent):
    
    ## @brief Instanciate a new EmField
    # @param uid str : uniq identifier
    # @param display_name MlString|str|dict : field display_name
    # @param data_handler class|str : A DataHandler class or display_name
    # @param help_text MlString|str|dict : help text
    # @param group EmGroup :
    # @param **handler_kwargs : data handler arguments
    def __init__(self, uid, data_handler, display_name = None, help_text = None, group = None, **handler_kwargs):
        super().__init__(uid, display_name, help_text, group)
        self.data_handler = data_handler
        self.data_handler_options = handler_kwargs
        ## @brief Stores the emclass that contains this field (set by EmClass.add_field() method)
        self._emclass = None

    ## @warning Not complete !
    # @todo Complete the hash when data handlers becomes available
    def d_hash(self):
        return int.from_bytes(hashlib.md5(
                        bytes(
                                "%s%s" % (  super().d_hash(),
                                            self.data_handler), 
                                'utf-8')
        ).digest(), byteorder='big')


## @brief Handles functionnal group of EmComponents
class EmGroup(object):
        
    ## @brief Create a new EmGroup
    # @note you should NEVER call the constructor yourself. Use Model.add_group instead
    # @param uid str : Uniq identifier
    # @param depends list : A list of EmGroup dependencies
    # @param display_name MlString|str : 
    # @param help_text MlString|str : 
    def __init__(self, uid, depends = None, display_name = None, help_text = None):
        self.uid = uid
        ## @brief Stores the list of groups that depends on this EmGroup indexed by uid
        self.required_by = dict()
        ## @brief Stores the list of dependencies (EmGroup) indexed by uid
        self.require = dict()
        ## @brief Stores the list of EmComponent instances contained in this group
        self.__components = set()

        self.display_name = None if display_name is None else MlString(display_name)
        self.help_text = None if help_text is None else MlString(help_text)
        if depends is not None:
            for grp in depends:
                if not isinstance(grp, EmGroup):
                    raise ValueError("EmGroup expected in depends argument but %s found" % grp)
                self.add_dependencie(grp)
    
    ## @brief Returns EmGroup dependencie
    # @param recursive bool : if True return all dependencies and their dependencies
    # @return a dict of EmGroup identified by uid
    def dependencies(self, recursive = False):
        res = copy.copy(self.require)
        if not recursive:
            return res
        to_scan = list(res.values())
        while len(to_scan) > 0:
            cur_dep = to_scan.pop()
            for new_dep in cur_dep.require.values():
                if new_dep not in res:
                    to_scan.append(new_dep)
                    res[new_dep.uid] = new_dep
        return res

    ## @brief Add components in a group
    # @param components list : EmComponent instance list
    def add_components(self, components):
        for component in components:
            if isinstance(component, EmField):
                if component._emclass is None:
                    warnings.warn("Adding an orphan EmField to an EmGroup")
            elif not isinstance(component, EmClass):
                raise EditorialModelError("Expecting components to be a list of EmComponent, but %s found in the list" % type(component))
        self.__components |= set(components)

    ## @brief Add a dependencie
    # @param em_group EmGroup|iterable : an EmGroup instance or list of instance
    def add_dependencie(self, grp):
        try:
            for group in grp:
                self.add_dependencie(group)
            return
        except TypeError: pass
                
        if grp.uid in self.require:
            return
        if self.__circular_dependencie(grp):
            raise EditorialModelError("Circular dependencie detected, cannot add dependencie")
        self.require[grp.uid] = grp
        grp.required_by[self.uid] = self
    
    ## @brief Search for circular dependencie
    # @return True if circular dep found else False
    def __circular_dependencie(self, new_dep):
        return self.uid in new_dep.dependencies(True)

    ## @brief Fancy string representation of an EmGroup
    # @return a string
    def __str__(self):
        if self.display_name is None:
            return self.uid
        else:
            return self.display_name.get()

    def d_hash(self):
        
        payload = "%s%s%s" % (self.uid, hash(self.display_name), hash(self.help_text))
        for recurs in (False, True):
            deps = self.dependencies(recurs)
            for dep_uid in sorted(deps.keys()):
                payload += str(deps[dep_uid].d_hash())
        for req_by_uid in self.required_by:
            payload += req_by_uid
        return int.from_bytes(
                                bytes(payload, 'utf-8'),
                                byteorder = 'big'
        )
    
    ## @brief Complete string representation of an EmGroup
    # @return a string
    def __repr__(self):
        return "<class EmGroup '%s' depends : [%s]>" % (self.uid, ', '.join([duid for duid in self.dependencies(False)]) )
