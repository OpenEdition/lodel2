#-*- coding:utf-8 -*-

import hashlib

from lodel.utils.mlstring import MlString

from lodel.editorial_model.exceptions import *
from lodel.editorial_model.components import EmClass, EmField, EmGroup

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
            return self.__elt_getter(self.__classes, uid)
        except KeyError:
            raise EditorialModelException("EmClass not found : '%s'" % uid)

    ## @brief EmGroup getter
    # @param uid None | str : give this argument to get a specific EmGroup
    # @return if uid given return an EmGroup else return an EmGroup iterator
    def groups(self, uid = None):
        try:
            return self.__elt_getter(self.__groups, uid)
        except KeyError:
            raise EditorialModelException("EmGroup not found : '%s'" % uid)

    ## @brief Add a class to the editorial model
    # @param emclass EmClass : the EmClass instance to add
    # @return emclass
    def add_class(self, emclass):
        if not isinstance(emclass, EmClass):
            raise ValueError("<class EmClass> expected but got %s " % type(emclass))
        if emclass.uid in self.classes():
            raise EditorialModelException('Duplicated uid "%s"' % emclass.uid)
        self.__classes[emclass.uid] = emclass
        return emclass

    ## @brief Add a group to the editorial model
    # @param emgroup EmGroup : the EmGroup instance to add
    # @return emgroup
    def add_group(self, emgroup):
        if not isinstance(emgroup, EmGroup):
            raise ValueError("<class EmGroup> expected but got %s" % type(emgroup))
        if emgroup.uid in self.groups():
            raise EditorialModelException('Duplicated uid "%s"' % emgroup.uid)
        self.__groups[emgroup.uid] = emgroup
        return emgroup

    ## @brief Add a new EmClass to the editorial model
    # @param uid str : EmClass uid
    # @param **kwargs : EmClass constructor options ( see @ref lodel.editorial_model.component.EmClass.__init__() )
    def new_class(self, uid, **kwargs):
        return self.add_class(EmClass(uid, **kwargs))
    
    ## @brief Add a new EmGroup to the editorial model
    # @param uid str : EmGroup uid
    # @param *kwargs : EmGroup constructor keywords arguments (see @ref lodel.editorial_model.component.EmGroup.__init__() )
    def new_group(self, uid, **kwargs):
        return self.add_group(EmGroup(uid, **kwargs))

    # @brief Save a model
    # @param translator module : The translator module to use
    # @param **translator_args
    def save(self, translator, **translator_kwargs):
        return translator.save(self, **translator_kwargs)
    
    ## @brief Load a model
    # @param translator module : The translator module to use
    # @param **translator_args
    @classmethod
    def load(cls, translator, **translator_kwargs):
        return translator.load(**translator_kwargs)
    
    ## @brief Private getter for __groups or __classes
    # @see classes() groups()
    def __elt_getter(self, elts, uid):
        return list(elts.values()) if uid is None else elts[uid]
    
    ## @brief Lodel hash
    def d_hash(self):
        payload = "%s%s" % (
                            self.name,
                            'NODESC' if self.description is None else self.description.d_hash()
        )
        for guid in sorted(self.__groups):
            payload += str(self.__groups[guid].d_hash())
        for cuid in sorted(self.__classes):
            payload += str(self.__classes[cuid].d_hash())
        return int.from_bytes(
                                hashlib.md5(bytes(payload, 'utf-8')).digest(),
                                byteorder='big'
        )

