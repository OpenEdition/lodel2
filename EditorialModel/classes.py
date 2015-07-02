# -*- coding: utf-8 -*-

## @file classes.py
# @see EditorialModel::classes::EmClass

import logging as logger

from EditorialModel.components import EmComponent, EmComponentNotExistError, EmComponentExistError
from Database import sqlutils
import sqlalchemy as sql

import EditorialModel.fieldtypes as ftypes
import EditorialModel


## @brief Manipulate Classes of the Editorial Model
# Create classes of object.
#@see EmClass, EmType, EmFieldGroup, EmField
class EmClass(EmComponent):

    table = 'em_class'
    ranked_in = 'classtype'

    ## @brief Specific EmClass fields
    # @see EditorialModel::components::EmComponent::_fields
    _fields = [
        ('classtype', ftypes.EmField_char),
        ('icon', ftypes.EmField_integer),
        ('sortcolumn', ftypes.EmField_char)
    ]

    ## Create a new class
    # @param name str: name of the new class
    # @param class_type EmClasstype: type of the class
    # @return An EmClass instance
    # @throw EmComponentExistError if an EmClass with this name and a different classtype exists
    # @todo Check class_type argument
    @classmethod
    def create(cls, name, class_type):
        return cls._create_db(name, class_type)

    @classmethod
    ## Isolate SQL for EmClass::create
    # @todo Remove hardcoded default value for icon
    # @return An instance of EmClass
    def _create_db(cls, name, class_type):
        #Create a new entry in the em_class table
        values = {'name': name, 'classtype': class_type['name'], 'icon': 0}
        resclass = super(EmClass, cls).create(**values)

        dbe = cls.db_engine()
        conn = dbe.connect()

        #Create a new table storing LodelObjects of this EmClass
        meta = sql.MetaData()
        emclasstable = sql.Table(resclass.class_table_name, meta, sql.Column('uid', sql.VARCHAR(50), primary_key=True))
        emclasstable.create(conn)

        conn.close()

        return resclass

    @property
    ## @brief Return the table name used to stores data on this class
    def class_table_name(self):
        return self.name

    ## @brief Delete a class if it's ''empty''
    # If a class has no fieldgroups delete it
    # @return bool : True if deleted False if deletion aborded
    def delete(self):
        do_delete = True
        fieldgroups = self.fieldgroups()
        if len(fieldgroups) > 0:
            do_delete = False
            return False

        dbe = self.__class__.db_engine()
        meta = sqlutils.meta(dbe)
        #Here we have to give a connection
        class_table = sql.Table(self.name, meta)
        meta.drop_all(tables=[class_table], bind=dbe)
        return super(EmClass, self).delete()


    ## Retrieve list of the field_groups of this class
    # @return A list of fieldgroups instance
    def fieldgroups(self):
        records = self._fieldgroups_db()
        fieldgroups = [EditorialModel.fieldgroups.EmFieldGroup(int(record.uid)) for record in records]

        return fieldgroups

    ## Isolate SQL for EmClass::fieldgroups
    # @return An array of dict (sqlalchemy fetchall)
    def _fieldgroups_db(self):
        dbe = self.__class__.db_engine()
        emfg = sql.Table(EditorialModel.fieldgroups.EmFieldGroup.table, sqlutils.meta(dbe))
        req = emfg.select().where(emfg.c.class_id == self.uid)

        conn = dbe.connect()
        res = conn.execute(req)
        return res.fetchall()

    ## Retrieve list of fields
    # @return fields [EmField]:
    def fields(self):
        fieldgroups = self.fieldgroups()
        fields = []
        for fieldgroup in fieldgroups:
            fields += fieldgroup.fields()
        return fields

    ## Retrieve list of type of this class
    # @return types [EmType]:
    def types(self):
        records = self._types_db()
        types = [EditorialModel.types.EmType(int(record.uid)) for record in records]

        return types

    ## Isolate SQL for EmCLass::types
    # @return An array of dict (sqlalchemy fetchall)
    def _types_db(self):
        dbe = self.__class__.db_engine()
        emtype = sql.Table(EditorialModel.types.EmType.table, sqlutils.meta(dbe))
        req = emtype.select().where(emtype.c.class_id == self.uid)
        conn = dbe.connect()
        res = conn.execute(req)
        return res.fetchall()

    ## Add a new EmType that can ben linked to this class
    # @param  em_type EmType: type to link
    # @return success bool: done or not
    def link_type(self, em_type):
        table_name = self.name + '_' + em_type.name
        self._link_type_db(table_name)

        return True

    def _link_type_db(self, table_name):
        #Create a new table storing LodelObjects that are linked to this EmClass
        conn = self.__class__.db_engine().connect()
        meta = sql.MetaData()
        emlinketable = sql.Table(table_name, meta, sql.Column('uid', sql.VARCHAR(50), primary_key=True))
        emlinketable.create(conn)
        conn.close()

    ## Retrieve list of EmType that are linked to this class
    #  @return types [EmType]:
    def linked_types(self):
        return self._linked_types_db()

    def _linked_types_db(self):
        dbe = self.__class__.db_engine()
        meta = sql.MetaData()
        meta.reflect(dbe)

        linked_types = []
        for table in meta.tables.values():
            table_name_elements = table.name.split('_')
            if len(table_name_elements) == 2:
                linked_types.append(EditorialModel.types.EmType(table_name_elements[1]))

        return linked_types
