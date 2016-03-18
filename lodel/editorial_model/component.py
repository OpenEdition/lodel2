#-*- coding: utf-8 -*-

import itertools

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
    # @return An iterator on EmFields instances (if uid is None) else return an EmField instance
    def fields(self, uid = None, no_parents = False):
        fields = self.__fields if no_parents else self.__all_fields
        try:
            return iter(fields.values()) if uid is None else fields[uid]
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
    
    ## @brief Create a new EmField and add it to the EmClass
    # @param uid str : the EmField uniq id
    # @param **field_kwargs :  EmField constructor parameters ( see @ref EmField.__init__() ) 
    def new_field(self, uid, **field_kwargs):
        return self.add_field(EmField(uid, **kwargs))


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
        self.data_handler_options = data_handler_options

    
