#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fieldtypes import *
from EditorialModel.fields_types import Em_Field_Type
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType

from Database import sqlutils
from Database.sqlwrapper import SqlWrapper
from Database.sqlquerybuilder import SqlQueryBuilder
from Database.sqlalter import DropColumn

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
    # @param name str: Name of the field
    # @param fieldgroup EmFieldGroup: Field group in which the field is
    # @param fieldtype EmFieldType: Type of the field
    # @param optional int: is the field optional ? (default=0)
    # @param internal int: is the field internal ? (default=0)
    # @param rel_to_type_id int: default=0
    # @param rel_field_id int: default=0
    # @param icon int: default=0
    # @param kwargs dict: Dictionary of the values to insert in the field record
    #
    # @throw TypeError
    # @see EmComponent::__init__()
    # @staticmethod
    @classmethod
    def create(cls, name, fieldgroup, fieldtype, optional=0, internal=0, rel_to_type_id=0, rel_field_id=0, icon=0):
        try:
            exists = EmField(name)
        except EmComponentNotExistError:
            values = {
                'name': name,
                'fieldgroup_id': fieldgroup.uid,
                'fieldtype': fieldtype.name,
                'optional': optional,
                'internal': internal,
                'rel_to_type_id': rel_to_type_id,
                'rel_field_id': rel_field_id,
                'icon': icon
            }

            created_field = super(EmField, cls).create(**values)
            if created_field:
                # The field was created, we then add its column in the corresponding class' table
                is_field_column_added = created_field.add_field_column_to_class_table()
                if is_field_column_added:
                    return created_field

            exists = created_field

        return exists
    
    ## @brief Delete a field if it's not linked
    # @return bool : True if deleted False if deletion aborded
    # @todo Check if unconditionnal deletion is correct
    def delete(self):
        dbe = self.__class__.getDbE()
        class_table = sql.Table(self.get_class_table(), sqlutils.meta(dbe))
        field_col = sql.Column(self.name)
        ddl = DropColumn(class_table, field_col)
        sqlutils.ddl_execute(ddl, self.__class__.getDbE())
        return super(EmField, self).delete()
    
    ## add_field_column_to_class_table (Function)
    #
    # Adds a column representing the field in its class' table
    #
    # @param emField EmField: the object representing the field
    # @return True in case of success, False if not
    def add_field_column_to_class_table(self):
        field_type = "%s%s" % (EditorialModel.fieldtypes.get_field_type(self.fieldtype).sql_column(), " DEFAULT 0" if self.fieldtype=='integer' else '')
        field_uid = self.uid
        field_class_table = self.get_class_table()
        return SqlWrapper().addColumn(tname=field_class_table, colname=self.name, coltype=field_type)

    ## get_class_table (Function)
    #
    # Gets the name of the table of the class corresponding to the field
    #
    # @return Name of the table
    def get_class_table(self):
        return self._get_class_table_db()

    ## _get_class_tableDb (Function)
    #
    # Executes a request to the database to get the name of the table in which to add the field
    #
    # @return Name of the table
    def _get_class_table_db(self):
        dbe = self.getDbE()
        conn = dbe.connect()
        fieldtable = sql.Table(EmField.table, sqlutils.meta(dbe))
        fieldgrouptable = sql.Table(EmFieldGroup.table, sqlutils.meta(dbe))
        reqGetClassId = fieldgrouptable.select().where(fieldgrouptable.c.uid == self.fieldgroup_id)
        resGetClassId = conn.execute(reqGetClassId).fetchall()
        class_id = dict(zip(resGetClassId[0].keys(), resGetClassId[0]))['class_id']

        classtable = sql.Table(EmClass.table, sqlutils.meta(dbe))
        reqGetClassTable = classtable.select().where(classtable.c.uid == class_id)
        resGetClassTable = conn.execute(reqGetClassTable).fetchall()
        classTableName = dict(zip(resGetClassTable[0].keys(), resGetClassTable[0]))['name']

        return classTableName

