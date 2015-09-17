#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
from EditorialModel.exceptions import EmComponentCheckError
import EditorialModel
from django.db import models

## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    ranked_in = 'fieldgroup_id'

    fieldtypes = {
        'int': models.IntegerField,
        'integer': models.IntegerField,
        'bigint': models.BigIntegerField,
        'smallint': models.SmallIntegerField,
        'boolean': models.BooleanField,
        'bool': models.BooleanField,
        'float': models.FloatField,
        'char': models.CharField,
        'varchar': models.CharField,
        'text': models.TextField,
        'time': models.TimeField,
        'date': models.DateField,
        'datetime': models.DateTimeField,
    }

    ## Instanciate a new EmField
    # @todo define and test type for icon and fieldtype
    def __init__(self, model, uid, name, fieldgroup_id, fieldtype, optional=False, internal=False, rel_to_type_id=None, rel_field_id=None, icon='0', string=None, help_text=None, date_update=None, date_create=None, rank=None, **kwargs):

        self.fieldgroup_id = fieldgroup_id
        self.check_type('fieldgroup_id', int)
        self.fieldtype = fieldtype
        self.optional = optional
        self.check_type('optional', bool)
        self.internal = internal
        self.check_type('internal', bool)
        self.rel_to_type_id = rel_to_type_id
        self.check_type('rel_to_type_id', (int, type(None)))
        self.rel_field_id = rel_field_id
        self.check_type('rel_field_id', (int, type(None)))
        self.icon = icon
        self.options = kwargs

        super(EmField, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

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

    def to_django(self):
        if self.fieldtype in ('varchar', 'char'):
            max_length = None if 'max_length' not in self.options else self.options['max_length']
            return self.fieldtypes[self.fieldtype](max_length=max_length, **self.options)

        if self.fieldtype in ('time', 'datetime', 'date'):
            auto_now = False if 'auto_now' not in self.options else self.options['auto_now']
            auto_now_add = False if 'auto_now_add' not in self.options else self.options['auto_now_add']
            return self.fieldtypes[self.fieldtype](auto_now=auto_now, auto_now_add=auto_now_add, **self.options)

        if self.fieldtype == 'boolean' and ('nullable' in self.options and self.options['nullable'] == 1):
            return models.NullBooleanField(**self.options)

        return self.fieldtypes[self.fieldtype](**self.options)
