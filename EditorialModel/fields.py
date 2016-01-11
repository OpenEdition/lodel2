#-*- coding: utf-8 -*-

import importlib
import warnings

from EditorialModel.components import EmComponent
from EditorialModel.exceptions import EmComponentCheckError
from EditorialModel.fieldtypes.generic import GenericFieldType
import EditorialModel
import EditorialModel.fieldtypes
#from django.db import models


## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    ranked_in = 'class_id'

    ## Instanciate a new EmField
    # @todo define and test type for icon
    # @warning nullable == True by default
    # @param model Model : Editorial model
    # @param uid int : Uniq id
    # @param fieldtype str : Fieldtype name ( see Editorialmodel::fieldtypes )
    # @param optional bool : Indicate if a field is optional or not
    # @param internal str|bool : If False the field is not internal, else it can takes value in "object" or "automatic"
    # @param rel_field_id int|None : If not None indicates that the field is a relation attribute (and the value is the UID of the rel2type field)
    # @param nullable bool : If True None values are allowed
    # @param uniq bool : if True the value should be uniq in the db table
    # @param **kwargs : more keywords arguments for the fieldtype
    def __init__(self, model, uid, name, class_id, fieldtype, optional=False, internal=False, rel_field_id=None, icon='0', string=None, help_text=None, date_update=None, date_create=None, rank=None, nullable=False, uniq=False, **kwargs):

        self.class_id = class_id
        self.check_type('class_id', int)
        self.optional = bool(optional)

        if not internal:
            self.internal = False
        else:
            if internal.lower() not in ['automatic', 'autosql']:
                raise ValueError("The internal arguments possible values are : [False, 'autosql', 'automatic']")
            self.internal = internal.lower()

        if self.internal == 'object' and name not in EditorialModel.classtypes.common_fields.keys():
            raise ValueError("Only common_fields are allowed to have the argument internal='object'")

        self.rel_field_id = rel_field_id
        self.check_type('rel_field_id', (int, type(None)))
        self.icon = icon

        #Field type elements
        self._fieldtype_cls = GenericFieldType.from_name(fieldtype)

        self.fieldtype = fieldtype
        self._fieldtype_args = kwargs
        self._fieldtype_args.update({'nullable': nullable, 'uniq': uniq, 'internal': self.internal})
        try:
            fieldtype_instance = self._fieldtype_cls(**self._fieldtype_args)
        except AttributeError as e:
            raise AttributeError("Error will instanciating fieldtype : %s" % e)

        if 'default' in kwargs:
            if not fieldtype_instance.check(default):
                raise TypeError("Default value ('%s') is not valid given the fieldtype '%s'" % (default, fieldtype))

        self.nullable = nullable
        self.uniq = uniq

        for kname, kval in kwargs.items():
            setattr(self, kname, kval)

        super(EmField, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    @staticmethod
    ## @brief Return the list of allowed field type
    def fieldtypes_list():
        return [f for f in EditorialModel.fieldtypes.__all__ if f != '__init__' and f != 'generic']

    ##@brief Return the EmFieldgroup this EmField belongs to
    @property
    def _fieldgroup(self):
        return self.model.component(self.fieldgroup_id)

    ## @brief Returns the EmClass this EmField belongs to
    @property
    def em_class(self):
        return self.model.component(self.class_id)

    ## @brief Get the fieldtype instance
    # @return a fieldtype instance
    def fieldtype_instance(self):
        return self._fieldtype_cls(**self._fieldtype_args)

    ## @brief Return the list of relation fields for a rel_to_type
    # @return None if the field is not a rel_to_type else return a list of EmField
    def rel_to_type_fields(self):
        if not self.rel_to_type_id:  # TODO Ajouter cette propriété
            return None

        return [f for f in self.model.components(EmField) if f.rel_field_id == self.uid]

    ## Check if the EmField is valid
    #
    # Check multiple things :
    # - the fieldgroup_id is valid
    # - the name is uniq in the EmClass
    # - if its a rel2type check that the linked_type is uniq in the EmClass
    # @return True if valid False if not
    def check(self):
        super(EmField, self).check()
        """
        #Fieldgroup check
        em_fieldgroup = self.model.component(self.fieldgroup_id)
        if not em_fieldgroup:
            raise EmComponentCheckError("fieldgroup_id contains a non existing uid : '%d'" % self.fieldgroup_id)
        if not isinstance(em_fieldgroup, EditorialModel.fieldgroups.EmFieldGroup):
            raise EmComponentCheckError("fieldgroup_id contains an uid from a component that is not an EmFieldGroup but a %s" % str(type(em_fieldgroup)))
        """
        #Uniq Name check
        if len([f for f in self.em_class.fields() if f.name == self.name]) > 1:
            raise EmComponentCheckError("The field %d has a name '%s' that is not uniq in the EmClass %d" % (self.uid, self.name, self.em_class.uid))
        #rel2type uniq check
        if self.fieldtype == 'rel2type':
            if len([f for f in self.em_class.fields() if f.fieldtype == 'rel2type' and f.rel_to_type_id == self.rel_to_type_id]) > 1:
                raise EmComponentCheckError("The rel2type %d is not uniq, another field is linked to the same type '%s' in the same class '%s'" % (self.uid, self.model.component(self.rel_to_type_id).name, self.em_class.name))

    ## @brief Delete a field if it's not linked
    # @return bool : True if deleted False if deletion aborded
    # @todo Check if unconditionnal deletion is correct
    def delete_check(self):
        return True
