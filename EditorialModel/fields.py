#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fieldtypes import *
from EditorialModel.fields_types import Em_Field_Type
from EditorialModel.fieldgroups import EmFieldGroup

from Database import sqlutils
from Database.sqlwrapper import SqlWrapper
from Database.sqlquerybuilder import SqlQueryBuilder

import sqlalchemy as sql

import EditorialModel
import logging

logger = logging.getLogger('Lodel2.EditorialModel')

## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    table = 'em_field'
    _fields = [
        ('fieldtype', EmField_char),
        ('fieldgroup_id', EmField_integer),
        ('rel_to_type_id', EmField_integer),
        ('rel_field_id', EmField_integer),
        ('optional', EmField_boolean),
        ('internal', EmField_boolean),
        ('icon', EmField_integer)
    ]

    ## Create (Function)
    #
    # Creates a new EmField and instanciates it
    #
    # @static
    #
    # @param name str: The name of the new Type
    # @param em_fieldgroup EmFieldGroup: The new field will belong to this fieldgroup
    # @param em_fieldtype EmFieldType: The new field will have this type
    # @param optional bool: Is the field optional ?
    # @param optional bool: Is the field internal ?
    #
    # @throw TypeError
    # @see EmComponent::__init__()
    # @staticmethod
    @classmethod
    def create(c, name, em_fieldgroup, em_fieldtype, optional=True, internal=False):
        try:
            exists = EmField(name)
        except EmComponentNotExistError:
            values = {
                #'uid' : None,
                'name' : name,
                'fieldgroup_id' : em_fieldgroup.uid,
                'fieldtype' : em_fieldtype.name,
                'optional' : 1 if optional else 0,
                'internal' : 1 if internal else 0,
                'rel_to_type_id': 0,
                'rel_field_id': 0,
                'icon':0
            }

            createdField = super(EmField,c).create(**values)
            if createdField:
                # The field was created, we then add its column in the corresponding class' table
                is_field_column_added = EmField.addFieldColumnToClassTable(createdField)
                if is_field_column_added:
                    return createdField

            exists = createdField

        return exists


    ## addFieldColumnToClassTable (Function)
    #
    # Adds a column representing the field in its class' table
    #
    # @static
    #
    # @param emField EmField: the object representing the field
    # @return True in case of success, False if not
    @classmethod
    def addFieldColumnToClassTable(c, emField):
        field_type = "%s%s" % (EditorialModel.fieldtypes.get_field_type(emField.fieldtype).sql_column(), " DEFAULT 0" if emField.fieldtype=='integer' else '')
        field_uid = emField.uid
        field_class_table = emField.get_class_table()
        return SqlWrapper().addColumn(tname=field_class_table, colname=emField.name, coltype=field_type)

    ## get_class_table (Function)
    #
    # Gets the name of the table of the class corresponding to the field
    #
    # @return Name of the table
    def get_class_table(self):
        return self._get_class_tableDb()

    ## _get_class_tableDb (Function)
    #
    # Executes a request to the database to get the name of the table in which to add the field
    #
    # @return Name of the table
    def _get_class_tableDb(self):
        dbe = self.getDbE()
        uidtable = sql.Table('uids', sqlutils.meta(dbe))
        conn = dbe.connect()
        req = uidtable.select().where(uidtable.c.uid==self.uid)
        records = conn.execute(req).fetchall()

        table_records = []
        for record in records:
            table_records.append(dict(zip(record.keys(), record)))
        table_record = table_records[0]
        table_name = table_record['table']

        return table_name

