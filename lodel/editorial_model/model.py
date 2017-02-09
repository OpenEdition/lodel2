#-*- coding:utf-8 -*-

import hashlib
import importlib
import copy

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.utils.mlstring': ['MlString'],
    'lodel.logger': 'logger',
    'lodel.settings': ['Settings'],
    'lodel.settings.utils': ['SettingsError'],
    'lodel.editorial_model.exceptions': ['EditorialModelError', 'assert_edit'],
    'lodel.editorial_model.components': ['EmClass', 'EmField', 'EmGroup']})


##@brief Describe an editorial model
#@ingroup lodel2_em
class EditorialModel(object):

    ##@brief if true we are in editor mode (all groups visible & loaded)
    #@note Usually comes from settings but can be overriden at runtime.
    #It as been implemented this way in order to allow to load EM
    #in lodelsites context (to generate dyncode for handled sites)
    _editormode = Settings.editorialmodel.editormode
    ##@brief When non in editor mode indicates the groups that we have to load
    #in our EM
    _groups = Settings.editorialmodel.groups

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

    ##@brief EmClass uids accessor
    #@return a dict of emclasses
    def all_classes(self, uid = None):
        if uid is None:
            return copy.copy(self.__classes)
        else:
            try:
                return copy.copy(self.__classes[uid])
            except KeyError:
                raise EditorialModelException("EmClass not found : '%s'" % uid)
    
    ##@brief EmClass instances accessor
    #@return a list of EmClass instances or a single EmClass instance
    def all_classes_ref(self, uid = None):
        if uid is None:
            return self.__classes
        else:
            try:
                return self.__classes[uid]
            except KeyError:
                raise EditorialModelException("EmGroup not found : '%s'" % uid)
                                
    ##@brief active EmClass uids accessor
    #@return a list of class uids
    def active_classes_uids(self):
            return list(self.__active_classes.keys())
        
    
    ##@brief EmGroups accessor
    #@return a dict of groups
    def all_groups(self, uid = None):
        if uid is None:
            return copy.copy(self.__groups)
        else:
            try:
                return copy.copy(self.__groups[uid])
            except KeyError:
                raise EditorialModelException("EmGroup not found : '%s'" % uid)
    
    ##@brief EmGroups accessor
    #@return a dict of groups
    def all_groups_ref(self, uid = None):
        if uid is None:
            return self.__groups
        else:
            try:
                return self.__groups[uid]
            except KeyError:
                raise EditorialModelException("EmGroup not found : '%s'" % uid)
                
    ##@brief active EmClass uids accessor
    #@return a list of class uids
    def active_groups_uids(self):
            return list(self.__active_groups.keys())

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
    
    ##@brief EmClass child list accessor
    #@param uid str : the EmClass uid
    #@return a set of EmClass
    def get_class_childs(self, uid):
        res = list()
        cur = self.classes(uid)
        for cls in self.classes():
            if cur in cls.parents_recc:
                res.append(cls)
        return set(res)

    ##@brief Allow to override class attributes _editormode and 
    #_groups in order to control groups exposure
    #
    #A typicall usage of this method is for lodelsites when updating
    #dyncode for handled sites. We have to set both attribute in order to
    #load the EM as wanted by the handled site.
    @classmethod
    def _override_settings(cls, editormode = False, groups = []):
        logger.warning("EM settings overriding ! If not in lodelsites \
context this is a REALLY BAD idea !")
        cls.__editormode = editormode
        cls.__groups = groups

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
        if self._editormode:
            logger.warning("All EM groups active because editormode in ON")
            # all groups & classes actives because we are in editor mode
            self.__active_groups = self.__groups
            self.__active_classes = self.__classes
        else:
            #determine groups first
            self.__active_groups = dict()
            self.__active_classes = dict()
            for agrp in self._groups:
                if agrp not in self.__groups:
                    raise SettingsError('Invalid group found in settings : %s' % agrp)
                logger.debug("Set group '%s' as active" % agrp)
                grp = self.__groups[agrp]
                self.__active_groups[grp.uid] = grp
                for acls in [cls for cls in grp.components() if isinstance(cls, EmClass)]:
                    self.__active_classes[acls.uid] = acls
            if len(self.__active_groups) == 0:
                raise RuntimeError("No groups activated, abording...")
            if len(self.__active_classes) == 0:
                raise RuntimeError("No active class found. Abording")
            for clsname, acls in self.__active_classes.items():
                acls._set_active_fields(self.__active_groups)
    
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
        assert_edit()
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
        assert_edit()
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
        assert_edit()
        return self.add_class(EmClass(uid, **kwargs))
    
    ##@brief Add a new EmGroup to the editorial model
    #@param uid str : EmGroup uid
    #@param *kwargs : EmGroup constructor keywords arguments (
    # see @ref lodel.editorial_model.component.EmGroup.__init__() )
    def new_group(self, uid, **kwargs):
        assert_edit()
        return self.add_group(EmGroup(uid, **kwargs))

    ##@brief Save a model
    # @param translator module : The translator module to use
    # @param **translator_args
    def save(self, translator, **translator_kwargs):
        assert_edit()
        if isinstance(translator, str):
            translator = self.translator_from_name(translator)
        return translator.save(self, **translator_kwargs)
    
    ##@brief Raise an error if lodel is not in EM edition mode
    @staticmethod
    def raise_if_ro():
        if not self._editormode:
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

