#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fieldtypes import *
from EditorialModel.fields_types import Em_Field_Type
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType

from Database import sqlutils
from Database.sqlwrapper import SqlWrapper
from Database.sqlalter import AddColumn
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
        ('fieldtype', EmField_char()),
        ('fieldtype_opt', EmField_char()),
        ('fieldgroup_id', EmField_integer()),
        ('rel_to_type_id', EmField_integer()),
        ('rel_field_id', EmField_integer()),
        ('optional', EmField_boolean()),
        ('internal', EmField_boolean()),
        ('icon', EmField_integer())
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
    def create(c, name, fieldgroup, fieldtype, optional=0, internal=0, rel_to_type_id=0, rel_field_id=0, icon=0):
        try:
            exists = EmField(name)
        except EmComponentNotExistError:
            values = {
                'name' : name,
                'fieldgroup_id' : fieldgroup.uid,
                'fieldtype' : fieldtype.__class__.__name__,
                'fieldtype_opt' : fieldtype.dump_opt(),
                'optional' : optional,
                'internal' : internal,
                'rel_to_type_id': rel_to_type_id,
                'rel_field_id': rel_field_id,
                'icon': icon
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
        tname = emField.get_class_table()
        ctable = sql.Table(tname, sqlutils.meta(c.getDbE()))
        ddl =  AddColumn(ctable, emField._fieldtype.sqlCol())
        return sqlutils.ddlExecute(ddl, c.getDbE())
    
    ## Set _fieldtype to the fieldtype instance
    def populate(self):
        super(EmField, self).populate()
        super(EmComponent, self).__setattr__('_fieldtype', EmFieldType.restore(self.name, self.fieldtype, self.fieldtype_opt))

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
        conn = dbe.connect()
        typetable = sql.Table(EmType.table, sqlutils.meta(dbe))
        fieldtable = sql.Table(EmField.table, sqlutils.meta(dbe))
        reqGetClassId = typetable.select().where(typetable.c.uid==fieldtable.c.rel_to_type_id)
        resGetClassId = conn.execute(reqGetClassId).fetchall()
        class_id = dict(zip(resGetClassId[0].keys(), resGetClassId[0]))['class_id']

        classtable = sql.Table(EmClass.table, sqlutils.meta(dbe))
        reqGetClassTable = classtable.select().where(classtable.c.uid == class_id)
        resGetClassTable = conn.execute(reqGetClassTable).fetchall()
        classTableName = dict(zip(resGetClassTable[0].keys(), resGetClassTable[0]))['name']

        return classTableName

