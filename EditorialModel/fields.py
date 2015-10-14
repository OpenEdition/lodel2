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

    ranked_in = 'fieldgroup_id'

    ## Instanciate a new EmField
    # @todo define and test type for icon and fieldtype
    # @warning nullable == True by default
    def __init__(self, model, uid, name, fieldgroup_id, fieldtype, optional=False, internal=False, rel_field_id=None, icon='0', string=None, help_text=None, date_update=None, date_create=None, rank=None, nullable=True, default=None, uniq=False, **kwargs):

        self.fieldgroup_id = fieldgroup_id
        self.check_type('fieldgroup_id', int)
        self.optional = optional
        self.check_type('optional', bool)
        self.internal = internal
        self.check_type('internal', bool)
        self.rel_field_id = rel_field_id
        self.check_type('rel_field_id', (int, type(None)))
        self.icon = icon

        #Field type elements
        self._fieldtype_cls = GenericFieldType.from_name(fieldtype)

        self.fieldtype = fieldtype
        self._fieldtype_args = kwargs
        self._fieldtype_args.update({'nullable' : nullable, 'default' : default, 'uniq' : uniq})
        self._fieldtype_instance = self._fieldtype_cls(**self._fieldtype_args)


        self.nullable = nullable
        self.default = default
        self.uniq = uniq
 
        for kname, kval in kwargs.items():
            setattr(self, kname, kval)

        super(EmField, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    @staticmethod
    ## @brief Return the list of allowed field type
    def fieldtypes_list():
        return [f for f in EditorialModel.fieldtypes.__all__ if f != '__init__']

    ## @brief Return the list of relation fields for a rel_to_type
    # @return None if the field is not a rel_to_type else return a list of EmField
    def rel_to_type_fields(self):
        if not self.rel_to_type_id:  # TODO Ajouter cette propriété
            return None

        return [f for f in self.model.components(EmField) if f.rel_field_id == self.uid]

    ## Check if the EmField is valid
    # @return True if valid False if not
    def check(self):
        super(EmField, self).check()
        em_fieldgroup = self.model.component(self.fieldgroup_id)
        if not em_fieldgroup:
            raise EmComponentCheckError("fieldgroup_id contains a non existing uid : '%d'" % self.fieldgroup_id)
        if not isinstance(em_fieldgroup, EditorialModel.fieldgroups.EmFieldGroup):
            raise EmComponentCheckError("fieldgroup_id contains an uid from a component that is not an EmFieldGroup but a %s" % str(type(em_fieldgroup)))

    ## @brief Delete a field if it's not linked
    # @return bool : True if deleted False if deletion aborded
    # @todo Check if unconditionnal deletion is correct
    def delete_check(self):
        return True
