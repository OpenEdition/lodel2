#-*- coding: utf-8 -*-

# @package lodel.editorial_model.components
#@brief Defines all @ref lodel2_em "EM" components
#@ingroup lodel2_em

import itertools
import warnings
import copy
import hashlib

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.utils.mlstring': ['MlString'],
    'lodel.mlnamedobject.mlnamedobject': ['MlNamedObject'],
    'lodel.settings': ['Settings'],
    'lodel.editorial_model.exceptions': ['EditorialModelError', 'assert_edit'],
    'lodel.leapi.leobject': ['CLASS_ID_FIELDNAME']})

## @brief Abstract class to represent editorial model components
# @see EmClass EmField
# @todo forbid '.' in uid
#@ingroup lodel2_em


class EmComponent(MlNamedObject):

    ## @brief Instanciate an EmComponent
    # @param uid str : uniq identifier
    # @param display_name MlString|str|dict : component display_name
    # @param help_text MlString|str|dict : help_text
    def __init__(self, uid, display_name=None, help_text=None, group=None):
        if self.__class__ == EmComponent:
            raise NotImplementedError('EmComponent is an abstract class')
        self.uid = uid
        self.group = group
        super().__init__(display_name, help_text)

    ## @brief Returns the display_name of the component if it is not None, its uid else
    def __str__(self):
        if self.display_name is None:
            return str(self.uid)
        return str(self.display_name)

    ## @brief Returns a hash code for the component
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


## @brief Handles editorial model objects classes
#@ingroup lodel2_em
class EmClass(EmComponent):

    ## @brief Instanciates a new EmClass
    #@param uid str : uniq identifier
    #@param display_name MlString|str|dict : component display_name
    #@param abstract bool : set the class as asbtract if True
    #@param pure_abstract bool : if True the EmClass will not be represented in
    # leapi dyncode
    #@param parents list: parent EmClass list or uid list
    #@param help_text MlString|str|dict : help_text
    #@param datasources str|tuple|list : The datasource name ( see
    #@ref lodel2_datasources ) or two names (first is read_only datasource the
    # second is read write)
    def __init__(
            self, uid, display_name=None, help_text=None, abstract=False,
            parents=None, group=None, pure_abstract=False,
            datasources='default'):

        super().__init__(uid, display_name, help_text, group)
        self.abstract = bool(abstract)
        self.pure_abstract = bool(pure_abstract)
        self.__datasource = datasources
        if not isinstance(datasources, str) and len(datasources) != 2:
            raise ValueError("datasources argument can be a single datasource\
 name or two names in a tuple or a list")
        if self.pure_abstract:
            self.abtract = True
        if parents is not None:
            if not isinstance(parents, list):
                parents = [parents]
            for parent in parents:
                if not isinstance(parent, EmClass):
                    raise ValueError(
                        "<class EmClass> expected in parents list, but %s found" % type(parent))
        else:
            parents = list()
        self.parents = parents
        ## @brief Stores EmFields instances indexed by field uid
        self.__fields = dict()

        self.group = group
        if group is None:
            warnings.warn("NO GROUP FOR EMCLASS %s" % uid)
        else:
            group.add_components([self])

        # Adding common field
        if not self.abstract:
            self.new_field(
                CLASS_ID_FIELDNAME,
                display_name={
                    'eng': "LeObject subclass identifier",
                    'fre': "Identifiant de la class fille de LeObject"},
                help_text={
                    'eng': "Allow to create instance of the good class when\
 fetching arbitrary datas from DB"},
                data_handler='LeobjectSubclassIdentifier',
                internal=True,
                group=group)

    ## @brief Property that represents a dict of all fields
    # (the EmField objects defined in this class and all their parents)
    # @todo use Settings.editorialmodel.groups to determine which fields should be returned
    @property
    def __all_fields(self):
        res = dict()
        for pfields in [p.__all_fields for p in self.parents]:
            res.update(pfields)
        res.update(self.__fields)
        return res

    ## @brief RO access to datasource attribute
    @property
    def datasource(self):
        return self.__datasource

    ## @brief Returns the list of all dependencies
    #
    # Recursive parents listing
    @property
    def parents_recc(self):
        if len(self.parents) == 0:
            return set()

        res = set(self.parents)
        for parent in self.parents:
            res |= parent.parents_recc
        return res

    ## @brief EmField getter
    # @param uid None | str : If None returns an iterator on EmField instances else return an EmField instance
    # @param no_parents bool : If True returns only fields defined is this class and not the one defined in parents classes
    # @return A list on EmFields instances (if uid is None) else return an EmField instance
    # @todo use Settings.editorialmodel.groups to determine wich fields should be returned
    def fields(self, uid=None, no_parents=False):
        fields = self.__fields if no_parents else self.__all_fields
        try:
            return list(fields.values()) if uid is None else fields[uid]
        except KeyError:
            raise EditorialModelError("No such EmField '%s'" % uid)

    ## @brief Keeps in __fields only fields contained in active groups
    def _set_active_fields(self, active_groups):
        if not Settings.editorialmodel.editormode:
            active_fields = []
            for grp_name, agrp in active_groups.items():
                active_fields += [emc for emc in agrp.components()
                                  if isinstance(emc, EmField)]
            self.__fields = {fname: fdh for fname, fdh in self.__fields.items()
                             if fdh in active_fields}

    ## @brief Adds a field to the EmClass
    # @param emfield EmField : an EmField instance
    # @warning do not add an EmField already in another class !
    # @throw EditorialModelException if an EmField with same uid already in this EmClass (overwriting allowed from parents)
    # @todo End the override checks (needs methods in data_handlers)
    def add_field(self, emfield):
        assert_edit()
        if emfield.uid in self.__fields:
            raise EditorialModelError(
                "Duplicated uid '%s' for EmField in this class ( %s )" % (emfield.uid, self))
        # Incomplete field override check
        if emfield.uid in self.__all_fields:
            parent_field = self.__all_fields[emfield.uid]
            if not emfield.data_handler_instance.can_override(parent_field.data_handler_instance):
                raise AttributeError(
                    "'%s' field overrides a parent field, but data_handlers are not compatible" % emfield.uid)
        self.__fields[emfield.uid] = emfield
        return emfield

    ## @brief Creates a new EmField and adds it to the EmClass
    # @param data_handler str : A DataHandler name
    # @param uid str : the EmField uniq id
    # @param **field_kwargs :  EmField constructor parameters ( see @ref EmField.__init__() )
    def new_field(self, uid, data_handler, **field_kwargs):
        assert_edit()
        return self.add_field(EmField(uid, data_handler, self, **field_kwargs))

    def d_hash(self):
        m = hashlib.md5()
        payload = str(super().d_hash()) + ("1" if self.abstract else "0")

        for p in sorted(self.parents):
            payload += str(p.d_hash())
        for fuid in sorted(self.__fields.keys()):
            payload += str(self.__fields[fuid].d_hash())

        m.update(bytes(payload, 'utf-8'))
        return int.from_bytes(m.digest(), byteorder='big')

    def __str__(self):
        return "<class EmClass %s>" % self.uid

    def __repr__(self):
        if not self.abstract:
            abstract = ''
        elif self.pure_abstract:
            abstract = 'PureAbstract'
        else:
            abstract = 'Abstract'
        return "<class %s EmClass uid=%s>" % (abstract, repr(self.uid))


## @brief Handles editorial model classes fields
#@ingroup lodel2_em
class EmField(EmComponent):

    ## @brief Instanciates a new EmField
    # @param uid str : uniq identifier
    # @param display_name MlString|str|dict : field display_name
    # @param data_handler str : A DataHandler name
    # @param help_text MlString|str|dict : help text
    # @param group EmGroup :
    # @param **handler_kwargs : data handler arguments
    def __init__(self, uid, data_handler, em_class=None, display_name=None, help_text=None, group=None, **handler_kwargs):
        from lodel.leapi.datahandlers.base_classes import DataHandler
        super().__init__(uid, display_name, help_text, group)
        ## @brief The data handler name
        self.data_handler_name = data_handler
        ## @brief The data handler class
        self.data_handler_cls = DataHandler.from_name(data_handler)
        ## @brief The data handler instance associated with this EmField
        self.data_handler_instance = self.data_handler_cls(**handler_kwargs)
        ## @brief Stores data handler instanciation options
        self.data_handler_options = handler_kwargs
        ## @brief Stores the emclass that contains this field (set by EmClass.add_field() method)
        self._emclass = em_class
        if self._emclass is None:
            warnings.warn("No EmClass for field %s" % uid)
        if group is None:
            warnings.warn("No EmGroup for field  %s" % uid)
        else:
            group.add_components([self])

    ## @brief Returns data_handler_name attribute
    def get_data_handler_name(self):
        return copy.copy(self.data_handler_name)

    ## @brief Returns data_handler_cls attribute
    def get_data_handler_cls(self):
        return copy.copy(self.data_handler_cls)

    ##@brief Returns the uid of the emclass which contains this field
    def get_emclass_uid(self):
        return self._emclass.uid

    # @warning Not complete !
    # @todo Complete the hash when data handlers becomes available
    def d_hash(self):
        return int.from_bytes(hashlib.md5(
            bytes(
                "%s%s%s" % (super().d_hash(),
                            self.data_handler_name,
                            self.data_handler_options),
                'utf-8')
        ).digest(), byteorder='big')

## @brief Handles functionnal group of EmComponents
#@ingroup lodel2_em


class EmGroup(MlNamedObject):

    ## @brief Creates a new EmGroup
    # @note you should NEVER call the constructor yourself. Use Model.add_group instead
    # @param uid str : Uniq identifier
    # @param depends list : A list of EmGroup dependencies
    # @param display_name MlString|str :
    # @param help_text MlString|str :
    def __init__(self, uid, depends=None, display_name=None, help_text=None):
        self.uid = uid
        ## @brief Stores the list of groups that depends on this EmGroup indexed by uid
        self.required_by = dict()
        ## @brief Stores the list of dependencies (EmGroup) indexed by uid
        self.require = dict()
        ## @brief Stores the list of EmComponent instances contained in this group
        self.__components = set()
        super().__init__(display_name, help_text)

        if depends is not None:
            for grp in depends:
                if not isinstance(grp, EmGroup):
                    raise ValueError("EmGroup expected in depends argument but %s found" % grp)
                self.add_dependency(grp)

    ## @brief Returns EmGroup dependencies
    # @param recursive bool : if True returns all dependencies and their own dependencies
    # @return a dict of EmGroup identified by uid
    def dependencies(self, recursive=False):
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

    ## @brief Returns EmGroup applicants
    # @param recursive bool : if True returns all dependencies and their dependencies
    # @returns a dict of EmGroup identified by uid
    def applicants(self, recursive=False):
        res = copy.copy(self.required_by)
        if not recursive:
            return res
        to_scan = list(res.values())
        while len(to_scan) > 0:
            cur_app = to_scan.pop()
            for new_app in cur_app.required_by.values():
                if new_app not in res:
                    to_scan.append(new_app)
                    res[new_app.uid] = new_app
        return res

    ## @brief Returns EmGroup components
    # @returns a copy of the set of components
    def components(self):
        return (self.__components).copy()

    ## @brief Returns EmGroup display_name
    #  @param lang str | None : If None returns default lang translation
    #  @returns None if display_name is None, a str for display_name else
    def get_display_name(self, lang=None):
        name = self.display_name
        if name is None:
            return None
        return name.get(lang)

    ## @brief Returns EmGroup help_text
    #  @param lang str | None : If None returns default lang translation
    #  @returns None if display_name is None, a str for display_name else
    def get_help_text(self, lang=None):
        help = self.help_text
        if help is None:
            return None
        return help.get(lang)

    ## @brief Adds components in a group
    # @param components list : EmComponent instances list
    def add_components(self, components):
        assert_edit()
        for component in components:
            if isinstance(component, EmField):
                if component._emclass is None:
                    msg = "Adding an orphan EmField '%s' to EmGroup '%s'"
                    msg %= (component, self)
                    warnings.warn(msg)
            elif not isinstance(component, EmClass):
                raise EditorialModelError(
                    "Expecting components to be a list of EmComponent, but %s found in the list" % type(component))
        self.__components |= set(components)

    ## @brief Add a dependency
    # @param em_group EmGroup|iterable : an EmGroup instance or list of instances
    def add_dependency(self, grp):
        assert_edit()
        try:
            for group in grp:
                self.add_dependency(group)
            return
        except TypeError:
            pass

        if grp.uid in self.require:
            return
        if self.__circular_dependency(grp):
            raise EditorialModelError("Circular dependencie detected, cannot add dependencie")
        self.require[grp.uid] = grp
        grp.required_by[self.uid] = self

    ## @brief Add a applicant
    # @param em_group EmGroup|iterable : an EmGroup instance or list of instance
    # Useless ???
    def add_applicant(self, grp):
        assert_edit()
        try:
            for group in grp:
                self.add_applicant(group)
            return
        except TypeError:
            pass

        if grp.uid in self.required_by:
            return
        if self.__circular_applicant(grp):
            raise EditorialModelError("Circular applicant detected, cannot add applicant")
        self.required_by[grp.uid] = grp
        grp.require[self.uid] = self

    ## @brief Search for circular dependency
    # @return True if circular dep found else False
    def __circular_dependency(self, new_dep):
        return self.uid in new_dep.dependencies(True)

    ## @brief Search for circular applicant
    # @return True if circular app found else False
    def __circular_applicant(self, new_app):
        return self.uid in new_app.applicants(True)

    ## @brief Fancy string representation of an EmGroup
    # @return a string
    def __str__(self):
        if self.display_name is None:
            return self.uid
        else:
            return self.display_name.get()

    ## @brief Computes a d-hash code for the EmGroup
    # @return a string
    def d_hash(self):

        payload = "%s%s%s" % (
            self.uid,
            'NODNAME' if self.display_name is None else self.display_name.d_hash(),
            'NOHELP' if self.help_text is None else self.help_text.d_hash()
        )
        for recurs in (False, True):
            deps = self.dependencies(recurs)
            for dep_uid in sorted(deps.keys()):
                payload += str(deps[dep_uid].d_hash())
        for req_by_uid in self.required_by:
            payload += req_by_uid
        return int.from_bytes(
            bytes(payload, 'utf-8'),
            byteorder='big'
        )

    ## @brief Complete string representation of an EmGroup
    # @return a string
    def __repr__(self):
        return "<class EmGroup '%s' depends : [%s]>" % (self.uid, ', '.join([duid for duid in self.dependencies(False)]))
