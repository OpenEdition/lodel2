#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Database import sqlutils

import sqlalchemy as sql

import EditorialModel

"""Represent one data for a lodel2 document"""
class EmField(EmComponent):

    table = 'em_field'

    def __init__(self, id_or_name):
        """ Instanciate an EmField with data fetched from db
            @param id_or_name str|int: Identify the EmType by name or by global_id
            @throw TypeError
            @see EmComponent::__init__()
        """
        self.table = EmField.table
        super(EmField, self).__init__(id_or_name)

    @classmethod
    def create(c, name, em_fieldgroup, em_fieldtype, optional=True, internal=False):
        """ Create a new EmField and instanciate it
            @static

            @param name str: The name of the new Type
            @param em_fieldgroup EmFieldGroup: The new field will belong to this fieldgroup
            @param ml_repr MlString|None: Multilingual representation of the type
            @param ml_help MlString|None: Multilingual help for the type
            @param The string|None: filename of the icon

            @param optional bool: Is the field optional ?
            @param internal bool: Is the field internal?

            @throw TypeError
            @see EmComponent::__init__()
            @staticmethod
        """
        try:
            exists = EmField(name)
        except EmComponentNotExistError:
            values = {
                'uid' : None,
                'name' : name,
                'fieldgroup_id' : em_fieldgroup.id,
                'fieldtype' : em_fieldtype.name,
                'optional' : 1 if optional else 0,
                'internal' : 1 if internal else 0,
            }
            return super(EmField,c).create(values)

        return exists


    """ Use dictionary (from database) to populate the object
    """
    def populate(self):
        row = super(EmField, self).populate()
        self.em_fieldgroup = EditorialModel.fieldgroups.EmFieldGroup(int(row.fieldgroup_id))
        self.em_fieldtype = EditorialModel.fieldtypes.get_field_type(row.fieldtype)
        self.optional = True if row.optional == 1 else False;
        self.internal = True if row.internal == 1 else False;
        self.icon = row.icon
        self.rel_to_type_id = EditorialModel.fieldtypes.EmFieldType(int(row.rel_to_type_id)) if row.rel_to_type_id else None
        self.rel_field_id = EmField(int(row.rel_field_id)) if row.rel_field_id else None

    def save(self):
        # should not be here, but cannot see how to do this
        if self.name is None:
            self.populate()

        values = {
            'fieldgroup_id' : self.em_fieldgroup.id,
            'fieldtype' : self.em_fieldtype.name,
            'optional' : 1 if self.optional else 0,
            'internal' : 1 if self.internal else 0,
            'icon' : self.icon,
            'rel_to_type_id' : self.rel_to_type_id.id if self.rel_to_type_id is not None else None,
            'rel_field_id' : self.rel_field_id.id if self.rel_field_id is not None else None
        }

        return super(EmField, self).save(values)
