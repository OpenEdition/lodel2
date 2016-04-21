#-*- coding:utf-8 -*-

import hashlib
import importlib

from lodel.utils.mlstring import MlString
from lodel.logger import logger
from lodel.settings import Settings
from lodel.settings.utils import SettingsError

from lodel.editorial_model.exceptions import *
from lodel.editorial_model.components import EmClass, EmField, EmGroup

##@brief Describe an editorial model
class EditorialModel(object):
    
    ##@brief Create a new editorial model
    # @param name MlString|str|dict : the editorial model name
    # @param description MlString|str|dict : the editorial model description
    def __init__(self, name, description = None):
        self.name = MlString(name)
        self.description = MlString(description)
        ##@brief Stores all groups indexed by id
        self.__groups = dict()
        ##@brief Stores all classes indexed by id
        self.__classes = dict()
        ## @brief Stores all activated groups indexed by id
        self.__active_groups = dict()
        ## @brief Stores all activated classes indexed by id
        self.__active_classes = dict()
        self.__set_actives()
    
    ##@brief EmClass accessor
    #@param uid None | str : give this argument to get a specific EmClass
    #@return if uid is given returns an EmClass else returns an EmClass
    # iterator
    #@todo use Settings.editorialmodel.groups to determine wich classes should
    # be returned
    def classes(self, uid = None):
        try:
            return self.__elt_getter(   self.__active_classes,
                                        uid)
        except KeyError:
            raise EditorialModelException("EmClass not found : '%s'" % uid)

    ##@brief EmGroup getter
    # @param uid None | str : give this argument to get a specific EmGroup
    # @return if uid is given returns an EmGroup else returns an EmGroup iterator
    def groups(self, uid = None):
        try:
            return self.__elt_getter(   self.__active_groups,
                                        uid)
        except KeyError:
            raise EditorialModelException("EmGroup not found : '%s'" % uid)
    
    ##@brief Private getter for __groups or __classes
    # @see classes() groups()
    def __elt_getter(self, elts, uid):
        return list(elts.values()) if uid is None else elts[uid]
    
    ##@brief Update the EditorialModel.__active_groups and
    #EditorialModel.__active_classes attibutes
    def __set_actives(self):
        if Settings.editorialmodel.editormode:
            # all groups & classes actives because we are in editor mode
            self.__active_groups = self.__groups
            self.__active_classes = self.__classes
        else:
            #determine groups first
            self.__active_groups = dict()
            for agrp in Settings.editorialmodel.groups:
                if agrp not in self.__groups:
                    raise SettingsError('Invalid group found in settings : %s' % agrp)
                grp = self.__groups[agrp]
                self.__active_groups[grp.uid] = grp
                for acls in grp.components():
                    self.__active_classes[acls.uid] = acls
    
    ##@brief EmField getter
    # @param uid str : An EmField uid represented by "CLASSUID.FIELDUID"
    # @return Fals or an EmField instance
    #
    # @todo delete it, useless...
    def field(self, uid = None):
        spl = uid.split('.')
        if len(spl) != 2:
            raise ValueError("Malformed EmField identifier : '%s'" % uid)
        cls_uid = spl[0]
        field_uid = spl[1]
        try:
            emclass = self.classes(cls_uid)
        except KeyError:
            return False
        try:
            return emclass.fields(field_uid)
        except KeyError:
            pass
        return False

    ##@brief Add a class to the editorial model
    # @param emclass EmClass : the EmClass instance to add
    # @return emclass
    def add_class(self, emclass):
        self.raise_if_ro()
        if not isinstance(emclass, EmClass):
            raise ValueError("<class EmClass> expected but got %s " % type(emclass))
        if emclass.uid in self.classes():
            raise EditorialModelException('Duplicated uid "%s"' % emclass.uid)
        self.__classes[emclass.uid] = emclass
        return emclass

    ##@brief Add a group to the editorial model
    # @param emgroup EmGroup : the EmGroup instance to add
    # @return emgroup
    def add_group(self, emgroup):
        self.raise_if_ro()
        if not isinstance(emgroup, EmGroup):
            raise ValueError("<class EmGroup> expected but got %s" % type(emgroup))
        if emgroup.uid in self.groups():
            raise EditorialModelException('Duplicated uid "%s"' % emgroup.uid)
        self.__groups[emgroup.uid] = emgroup
        return emgroup

    ##@brief Add a new EmClass to the editorial model
    #@param uid str : EmClass uid
    #@param **kwargs : EmClass constructor options ( 
    # see @ref lodel.editorial_model.component.EmClass.__init__() )
    def new_class(self, uid, **kwargs):
        self.raise_if_ro()
        return self.add_class(EmClass(uid, **kwargs))
    
    ##@brief Add a new EmGroup to the editorial model
    #@param uid str : EmGroup uid
    #@param *kwargs : EmGroup constructor keywords arguments (
    # see @ref lodel.editorial_model.component.EmGroup.__init__() )
    def new_group(self, uid, **kwargs):
        self.raise_if_ro()
        return self.add_group(EmGroup(uid, **kwargs))

    ##@brief Save a model
    # @param translator module : The translator module to use
    # @param **translator_args
    def save(self, translator, **translator_kwargs):
        self.raise_if_ro()
        if isinstance(translator, str):
            translator = self.translator_from_name(translator)
        return translator.save(self, **translator_kwargs)
    
    ##@brief Raise an error if lodel is not in EM edition mode
    @staticmethod
    def raise_if_ro():
        if not Settings.editorialmodel.editormode:
            raise EditorialModelError("Lodel in not in EM editor mode. The EM is in read only state")

    ##@brief Load a model
    # @param translator module : The translator module to use
    # @param **translator_args
    @classmethod
    def load(cls, translator, **translator_kwargs):
        if isinstance(translator, str):
            translator = cls.translator_from_name(translator)
        res = translator.load(**translator_kwargs)
        res.__set_actives()
        return res

    ##@brief Return a translator module given a translator name
    # @param translator_name str : The translator name
    # @return the translator python module
    # @throw NameError if the translator does not exists
    @staticmethod
    def translator_from_name(translator_name):
        pkg_name = 'lodel.editorial_model.translator.%s' % translator_name
        try:
            mod = importlib.import_module(pkg_name)
        except ImportError:
            raise NameError("No translator named %s")
        return mod
        
    ##@brief Lodel hash
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

