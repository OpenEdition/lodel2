#-*- coding: utf-8 -*-

import EditorialModel
from EditorialModel.components import EmComponent
from EditorialModel.fields import EmField
from EditorialModel.classtypes import EmClassType, EmNature
from EditorialModel.exceptions import MigrationHandlerChangeError, EmComponentCheckError
import EditorialModel.classes


## Represents type of documents
# A type is a specialisation of a class, it can select optional field,
# they have hooks, are organized in hierarchy and linked to other
# EmType with special fields called relation_to_type fields
#
# @see EditorialModel::components::EmComponent
# @todo sortcolumn handling
class EmType(EmComponent):
    ranked_in = 'class_id'

    ## Instanciate a new EmType
    # @todo define and check types for icon and sortcolumn
    # @todo better check self.subordinates
    def __init__(self, model, uid, name, class_id, fields_list=None, superiors_list=None, icon='0', sortcolumn='rank', string=None, help_text=None, date_update=None, date_create=None, rank=None):
        self.class_id = class_id
        self.check_type('class_id', int)
        self.fields_list = fields_list if fields_list is not None else []
        self.check_type('fields_list', list)
        for field_uid in self.fields_list:
            if not isinstance(field_uid, int):
                raise AttributeError("Excepted fields_list to be a list of integers, but found a " + str(type(field_uid)) + " in it")

        self.superiors_list = superiors_list if superiors_list is not None else {}
        self.check_type('superiors_list', dict)
        for nature, superiors_uid in self.superiors_list.items():
            if nature not in [EmNature.PARENT, EmNature.TRANSLATION, EmNature.IDENTITY]:
                raise AttributeError("Nature '%s' of superior is not allowed !" % nature)
            if not isinstance(superiors_uid, list):
                raise AttributeError("Excepted superiors of nature '%s' to be an list !" % nature)
            for superior_uid in superiors_uid:
                if not isinstance(superior_uid, int):
                    raise AttributeError("Excepted superiors_list of nature '%s' to be a list of integers, but found a '%s' in it" % str(type(superior_uid)))

        self.icon = icon
        self.sortcolumn = sortcolumn
        super(EmType, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    @classmethod
    ## Create a new EmType and instanciate it
    # @param name str: The name of the new type
    # @param em_class EmClass: The class that the new type will specialize
    # @param sortcolumn str : The name of the field that will be used to sort
    # @param **em_component_args : @ref EditorialModel::components::create()
    # @param cls
    # @return An EmType instance
    # @throw EmComponentExistError if an EmType with this name but different attributes exists
    # @see EmComponent::__init__()
    #
    # @todo check that em_class is an EmClass object (fieldtypes can handle it)
    def create(cls, name, em_class, sortcolumn='rank', **em_component_args):
        return super(EmType, cls).create(name=name, class_id=em_class.uid, sortcolumn=sortcolumn, **em_component_args)

    @property
    ## Return the EmClassType of the type
    # @return EditorialModel.classtypes.*
    def classtype(self):
        return getattr(EmClassType, self.em_class.classtype)

    @property
    ## Return an instance of the class this type belongs to
    # @return EditorialModel.EmClass
    def em_class(self):
        return self.model.component(self.class_id)

    ## @brief Delete an EmType
    # The deletion is only possible if a type is not linked by any EmClass
    # and if it has no subordinates
    # @return True if delete False if not deleted
    # @todo Check if the type is not linked by any EmClass
    # @todo Check if there is no other ''non-deletion'' conditions
    def delete_check(self):
        if len(self.subordinates()) > 0:
            return False
        #Delete all relation with superiors
        for nature, sups in self.superiors().items():
            for sup in sups:
                self.del_superior(sup, nature)
        return True

    ## Get the list of non empty associated fieldgroups
    # @return A list of EmFieldGroup instance
    def _fieldgroups(self):
        fieldgroups = [fieldgroup for fieldgroup in self.em_class.fieldgroups() if len(fieldgroup.fields(self.uid))]
        return fieldgroups

    ## Return selected optional field
    # @return A list of EmField instance
    def selected_fields(self):
        selected = [self.model.component(field_id) for field_id in self.fields_list]
        return selected

    ## Return the list of associated fields
    # @return A list of EmField instance
    def fields(self, relational = False):
        return [ field for field in self.em_class.fields() if not field.optional or (field.optional and field.uid in self.fields_list) ]

    ## Select_field (Function)
    #
    # Indicates that an optional field is used
    #
    # @param field EmField: The optional field to select
    #
    # @throw TypeError if field is not an EmField instance
    # @throw ValueError if field is not optional or is not associated with this type
    # @throw MigrationHandlerChangeError if migration handler is not happy with the change
    # @see EmType::_change_field_list()
    def select_field(self, field):
        if field.uid in self.fields_list:
            return True
        self._change_field_list(field, True)

    ## Unselect_field (Function)
    #
    # Indicates that an optional field will not be used
    #
    # @param field EmField: The optional field to unselect
    #
    # @throw TypeError if field is not an EmField instance
    # @throw ValueError if field is not optional or is not associated with this type
    # @throw MigrationHandlerChangeError if migration handler is not happy with the change
    # @see EmType::_change_field_list()
    def unselect_field(self, field):
        if field.uid not in self.fields_list:
            return True
        self._change_field_list(field, False)

    ## @brief Select or unselect an optional field
    # @param field EmField: The EmField to select or unselect
    # @param select bool: If True select field, else unselect it
    #
    # @throw TypeError if field is not an EmField instance
    # @throw ValueError if field is not optional or is not associated with this type
    # @throw MigrationHandlerChangeError if migration handler is not happy with the change
    def _change_field_list(self, field, select=True):
        if not isinstance(field, EmField):
            raise TypeError("Excepted <class EmField> as field argument. But got " + str(type(field)))
        if field not in self.em_class.fields():
            raise ValueError("This field " + str(field) + "is not part of the type " + str(self))
        if not field.optional:
            raise ValueError("This field is not optional")

        try:
            if select:
                self.fields_list.append(field.uid)
                self.model.migration_handler.register_change(self.model, self.uid, None, {'fields_list': field.uid})
            else:
                self.fields_list.remove(field.uid)
                self.model.migration_handler.register_change(self.model, self.uid, {'fields_list': field.uid}, None)
        except MigrationHandlerChangeError as exception_object:
            if select:
                self.fields_list.remove(field.uid)
            else:
                self.fields_list.append(field.uid)
            raise exception_object

        self.model.migration_handler.register_model_state(self.model, hash(self.model))

    ## Get the list of associated hooks
    # @note Not conceptualized yet
    # @todo Conception
    def hooks(self):
        raise NotImplementedError()

    ## Add a new hook
    # @param hook EmHook: An EmHook instance
    # @throw TypeError
    # @note Not conceptualized yet
    # @todo Conception
    def add_hook(self, hook):
        raise NotImplementedError()

    ## Delete a hook
    # @param hook EmHook: An EmHook instance
    # @throw TypeError
    # @note Not conceptualized yet
    # @todo Conception
    # @todo Maybe we don't need a EmHook instance but just a hook identifier
    def del_hook(self, hook):
        raise NotImplementedError()

    ## @brief Get the list of subordinates EmType
    # Get a list of EmType instance that have this EmType for superior
    # @return Return a dict with relation nature as keys and values as a list of subordinates
    # EmType instance
    # @throw RuntimeError if a nature fetched from db is not valid
    def subordinates(self):
        subordinates = {}
        for em_type in self.model.components(EmType):
            for nature, superiors_uid in em_type.superiors_list.items():
                if self.uid in superiors_uid:
                    if nature in subordinates:
                        subordinates[nature].append(em_type)
                    else:
                        subordinates[nature] = [em_type]
        return subordinates

    ## @brief Get the list of superiors by relation's nature
    # Get a list of EmType that are superiors of this type
    # @return Return a dict with relation nature as keys and an EmType as value
    # @throw RuntimeError if a nature has multiple superiors
    def superiors(self):
        return {nature: [self.model.component(superior_uid) for superior_uid in superiors_uid] for nature, superiors_uid in self.superiors_list.items()}

    ## @brief Given a relation's nature return all the possible type to add as superiors
    # @param relation_nature str | None : if None check for all natures
    # @return a list or a dict with nature as key
    def possible_superiors(self, relation_nature=None):
        if relation_nature is None:
            ret = {}
            for nat in EmNature.getall():
                ret[nat] = self.possible_superiors(nat)
            return ret

        #One nature
        if relation_nature not in self.classtype['hierarchy']:
            return []

        att = self.classtype['hierarchy'][relation_nature]['attach']
        if att == 'type':
            return [self]
        else:
            return [t for t in self.model.components(EmType) if t.classtype == self.classtype]

    ## Add a superior in the type hierarchy
    # @param em_type EmType: An EmType instance
    # @param relation_nature str: The name of the relation's nature
    # @return False if no modification made, True if modifications success
    #
    # @throw TypeError when em_type not an EmType instance
    # @throw ValueError when relation_nature isn't reconized or not allowed for this type
    # @throw ValueError when relation_nature don't allow to link this types together
    def add_superior(self, em_type, relation_nature):
        # check if relation_nature is valid for this type
        if relation_nature not in EmClassType.natures(self.classtype['name']):
            raise ValueError("Invalid nature for add_superior : '" + relation_nature + "'. Allowed relations for this type are " + str(EmClassType.natures(self.classtype['name'])))

        if relation_nature in self.superiors_list and em_type.uid in self.superiors_list[relation_nature]:
            return True

        att = self.classtype['hierarchy'][relation_nature]['attach']
        if att == 'classtype':
            if self.classtype['name'] != em_type.classtype['name']:
                raise ValueError("Not allowed to put an em_type with a different classtype as superior")
        elif self.name != em_type.name:
            raise ValueError("Not allowed to put a different em_type as superior in a relation of nature '" + relation_nature + "'")

        self._change_superiors_list(em_type, relation_nature, True)

    ## Delete a superior in the type hierarchy
    # @param em_type EmType: An EmType instance
    # @param relation_nature str: The name of the relation's nature
    # @throw TypeError when em_type isn't an EmType instance
    # @throw ValueError when relation_nature isn't reconized or not allowed for this type
    def del_superior(self, em_type, relation_nature):
        if relation_nature not in self.superiors_list or em_type.uid not in self.superiors_list[relation_nature]:
            return True
        self._change_superiors_list(em_type, relation_nature, False)

    ## Apply changes to the superiors_list
    # @param em_type EmType: An EmType instance
    # @param relation_nature str: The name of the relation's nature
    # @param add bool: Add or delete relation
    def _change_superiors_list(self, em_type, relation_nature, add=True):
        # check instance of parameters
        if not isinstance(em_type, EmType) or not isinstance(relation_nature, str):
            raise TypeError("Excepted <class EmType> and <class str> as em_type argument. But got : " + str(type(em_type)) + " " + str(type(relation_nature)))

        try:
            if add:
                if relation_nature in self.superiors_list:
                    self.superiors_list[relation_nature].append(em_type.uid)
                else:
                    self.superiors_list[relation_nature] = [em_type.uid]
                self.model.migration_handler.register_change(self.model, self.uid, None, {'superiors_list': {relation_nature: em_type.uid}})
            else:
                self.superiors_list[relation_nature].remove(em_type.uid)
                if len(self.superiors_list[relation_nature]) == 0:
                    del self.superiors_list[relation_nature]
                self.model.migration_handler.register_change(self.model, self.uid, {'superiors_list': {relation_nature: em_type.uid}}, None)
        # roll-back
        except MigrationHandlerChangeError as exception_object:
            if add:
                self.superiors_list[relation_nature].remove(em_type.uid)
                if len(self.superiors_list[relation_nature]) == 0:
                    del self.superiors_list[relation_nature]
            else:
                if relation_nature in self.superiors_list:
                    self.superiors_list[relation_nature].append(em_type.uid)
                else:
                    self.superiors_list[relation_nature] = [em_type.uid]
            raise exception_object

        self.model.migration_handler.register_model_state(self.model, hash(self.model))

    ## Checks if the EmType is valid
    # @throw EmComponentCheckError if check fails
    def check(self):
        super(EmType, self).check()
        em_class = self.model.component(self.class_id)
        if not em_class:
            raise EmComponentCheckError("class_id contains an uid that does not exists '%d'" % self.class_id)
        if not isinstance(em_class, EditorialModel.classes.EmClass):
            raise EmComponentCheckError("class_id contains an uid from a component that is not an EmClass but a %s" % str(type(em_class)))

        for i, f_uid in enumerate(self.fields_list):
            field = self.model.component(f_uid)
            if not field:
                raise EmComponentCheckError("The element %d of selected_field is a non existing uid '%d'" % (i, f_uid))
            if not isinstance(field, EmField):
                raise EmComponentCheckError("The element %d of selected_field is not an EmField but a %s" % (i, str(type(field))))
            if not field.optional:
                raise EmComponentCheckError("The element %d of selected_field is an EmField not optional" % i)
            """
            if field.fieldgroup_id not in [fg.uid for fg in self.fieldgroups()]:
                raise EmComponentCheckError("The element %d of selected_field is an EmField that is part of an EmFieldGroup that is not associated with this EmType" % i)
            """

        for nature, superiors_uid in self.superiors_list.items():
            for superior_uid in superiors_uid:
                em_type = self.model.component(superior_uid)
                if not em_type:
                    raise EmComponentCheckError("The superior is a non existing uid '%d'" % (superior_uid))
                if not isinstance(em_type, EmType):
                    raise EmComponentCheckError("The superior is a component that is not an EmType but a %s" % (str(type(em_type))))
                if nature not in EmClassType.natures(self.em_class.classtype):
                    raise EmComponentCheckError("The relation nature '%s' of the superior is not valid for this EmType classtype '%s'", (nature, self.classtype))

                nat_spec = getattr(EmClassType, self.em_class.classtype)['hierarchy'][nature]

                if nat_spec['attach'] == 'classtype':
                    if self.classtype != em_type.classtype:
                        raise EmComponentCheckError("The superior is of '%s' classtype. But the current type is of '%s' classtype, and relation nature '%s' require two EmType of same classtype" % (em_type.classtype, self.classtype, nature))
                elif nat_spec['attach'] == 'type':
                    if self.uid != em_type.uid:
                        raise EmComponentCheckError("The superior is a different EmType. But the relation nature '%s' require the same EmType" % (nature))
                else:
                    raise NotImplementedError("The nature['attach'] '%s' is not implemented in this check !" % nat_spec['attach'])

                if 'max_depth' in nat_spec and nat_spec['max_depth'] > 0:
                    depth = 1
                    cur_type = em_type
                    while depth >= nat_spec['max_depth']:
                        depth += 1
                        if len(cur_type.subordinates()[nature]) == 0:
                            break
                    else:
                        raise EmComponentCheckError("The relation with superior %d  has a depth superior than the maximum depth (%d) allowed by the relation's nature '%s'" % (superior_uid, nat_spec['max_depth'], nature))

        for nature in self.subordinates():
            nat_spec = getattr(EmClassType, self.em_class.classtype)['hierarchy'][nature]
            if 'max_child' in nat_spec and nat_spec['max_child'] > 0:
                if len(self.subordinates()[nature]) > nat_spec['max_child']:
                    raise EmComponentCheckError("The EmType has more child than allowed in the relation's nature : %d > %d" % (len(self.subordinates()[nature], nat_spec['max_child'])))
