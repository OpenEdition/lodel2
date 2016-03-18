#-*- coding:utf-8 -*-
from lodel.utils.mlstring import MlString

from lodel.editorial_model.exceptions import *
from lodel.editorial_model.component import EmClass, EmField

## @brief Describe an editorial model
class EditorialModel(object):
    
    ## @brief Create a new editorial model
    # @param name MlString|str|dict : the editorial model name
    # @param description MlString|str|dict : the editorial model description
    def __init__(self, name, description = None):
        self.name = MlString(name)
        self.description = MlString(description)
        ## @brief Stores all groups indexed by id
        self.__groups = dict()
        ## @brief Stores all classes indexed by id
        self.__classes = dict()
    
    ## @brief EmClass accessor
    # @param uid None | str : give this argument to get a specific EmClass
    # @return if uid given return an EmClass else return an EmClass iterator
    def classes(self, uid = None):
        try:
            return __elt_getter(self.__classes)
        except KeyError:
            raise EditorialModelException("EmClass not found : '%s'" % uid)

    ## @brief EmGroup getter
    # @param uid None | str : give this argument to get a specific EmGroup
    # @return if uid given return an EmGroup else return an EmGroup iterator
    def groups(self, uid = None):
        try:
            return __elt_getter(self.__groups)
        except KeyError:
            raise EditorialModelException("EmGroup not found : '%s'" % uid)

    ## @brief Add a class to the editorial model
    # @param emclass EmClass : the EmClass instance to add
    def add_class(self, emclass):
        if not isinstance(emclass, EmClass):
            raise ValueError("<class EmClass> expected but got %s " % type(emclass))
        if emclass.uid in self.classes:
            raise EditorialModelException('Duplicated uid "%s"' % emclass.uid)
        self.__classes[emclass.uid] = emclass

    ## @brief Add a new EmClass to the editorial model
    # @param uid str : EmClass uid
    # @param **kwargs : EmClass constructor options ( see @ref lodel.editorial_model.component.EmClass.__init__() )
    def new_class(self, uid, **kwargs):
        return self.add_class(EmClass(uid, **kwargs))

    # @brief Save a model
    # @param translator module : The translator module to use
    # @param **translator_args
    def save(self, translator, **translator_args):
        return translator.save(self, **kwargs)
    
    ## @brief Load a model
    # @param translator module : The translator module to use
    # @param **translator_args
    @classmethod
    def load(cls, translator, **translator_args):
        return translator.load(**kwargs)
    
    ## @brief Private getter for __groups or __classes
    # @see classes() groups()
    def __elt_getter(self, elts, uid):
        return iter(elts.values) if uid is None else elts[uid]

