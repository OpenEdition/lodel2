#-*- coding: utf-8 -*-

import importlib
import warnings

from EditorialModel.components import EmComponent
from EditorialModel.exceptions import EmComponentCheckError
import EditorialModel
import EditorialModel.fieldtypes
from django.db import models

## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    ranked_in = 'fieldgroup_id'

    ftype = None
    help = 'Default help text'

    ## Instanciate a new EmField
    # @todo define and test type for icon and fieldtype
    # @warning nullable == True by default
    def __init__(self, model, uid, name, fieldgroup_id, fieldtype, optional=False, internal=False, rel_field_id=None, icon='0', string=None, help_text=None, date_update=None, date_create=None, rank=None, nullable = True, default = None, uniq = False, **kwargs):

        if self.ftype == None:
            raise NotImplementedError("Trying to instanciate an EmField and not one of the fieldtypes child classes")

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
        self.fieldtype = fieldtype
        self.nullable = nullable
        self.default = default
        self.uniq = uniq

        if len(kwargs) > 0:
            for kwargs_f in kwargs:
                warnings.warn("Argument '%s' not used and will be invalid for EmField __init__"%kwargs_f,SyntaxWarning)
            

        super(EmField, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    @staticmethod
    ## @brief Return an EmField subclass given a wanted field type
    # @return An EmField subclass
    # @throw When not found
    # @see EmField::fieldtypes()
    def get_field_class(ftype, **kwargs):
        if ftype == 'integer':
            ftype_module = importlib.import_module('EditorialModel.fieldtypes.int')
        else:
            ftype_module = importlib.import_module('EditorialModel.fieldtypes.%s'%ftype)

        return ftype_module.fclass

    @staticmethod
    ## @brief Return the list of allowed field type
    def fieldtypes_list():
        return [ f for f in EditorialModel.fieldtypes.__all__ if f != '__init__' ]

    ## @brief Abstract method that should return a validation function
    # @param raise_e Exception : if not valid raise this exception
    # @param ret_valid : if valid return this value
    # @param ret_invalid : if not valid return this value
    def validation_function(self, raise_e = None, ret_valid = None, ret_invalid = None):
        if self.__class__ == EmField:
            raise NotImplementedError("Abstract method")
        if raise_e is None and ret_valid is None:
            raise AttributeError("Behavior doesn't allows to return a valid validation function")

        return False
            

    ## @brief Return the list of relation fields for a rel_to_type
    # @return None if the field is not a rel_to_type else return a list of EmField
    def rel_to_type_fields(self):
        if not self.rel_to_type_id:
            return None
        
        return [ f for f in self.model.components(EmField) if f.rel_field_id == self.uid ]

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

