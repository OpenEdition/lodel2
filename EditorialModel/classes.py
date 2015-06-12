# -*- coding: utf-8 -*-

""" Manipulate Classes of the Editorial Model
    Create classes of object
    @see EmClass, EmType, EmFieldGroup, EmField
"""

import logging as logger

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Database import sqlutils
import sqlalchemy as sql

import EditorialModel.fieldtypes as ftypes

class EmClass(EmComponent):
    table = 'em_class'

    def __init__(self, id_or_name):
        self.table = EmClass.table
        self._fields = [('classtype', ftypes.EmField_char()), ('icon', ftypes.EmField_integer()), ('sortcolumn', ftypes.EmField_char())]
        super(EmClass, self).__init__(id_or_name)

    """ create a new class
        @param name str: name of the new class
        @param class_type EmClasstype: type of the class
    """
    @classmethod
    def create(c, name, class_type):
        try:
            res = EmClass(name)
            logger.info("Trying to create an EmClass that allready exists")
        except EmComponentNotExistError:
            res = c._createDb(name, class_type)
            logger.debug("EmClass successfully created")

        return res

    @classmethod
    def _createDb(c, name, class_type):
        """ Do the db querys for EmClass::create() """

        #Create a new entry in the em_class table
        values = { 'name':name, 'classtype':class_type['name'] }
        resclass = super(EmClass,c).create(values)


        dbe = c.getDbE()
        conn = dbe.connect()

        #Create a new table storing LodelObjects of this EmClass
        meta = sql.MetaData()
        emclasstable = sql.Table(name, meta,
            sql.Column('uid', sql.VARCHAR(50), primary_key = True))
        emclasstable.create(conn)

        conn.close()

        return resclass


    """ retrieve list of the field_groups of this class
        @return field_groups [EmFieldGroup]:
    """
    def fieldgroups(self):
        records = self._fieldgroupsDb()
        fieldgroups = [ EditorialModel.fieldgroups.EmFieldGroup(int(record.uid)) for record in records ]

        return fieldgroups

    def _fieldgroupsDb(self):
        dbe = self.__class__.getDbE()
        emfg = sql.Table(EditorialModel.fieldgroups.EmFieldGroup.table, sqlutils.meta(dbe))
        req = emfg.select().where(emfg.c.class_id == self.id)

        conn = dbe.connect()
        res = conn.execute(req)
        return res.fetchall()


    """ retrieve list of fields
        @return fields [EmField]:
    """
    def fields(self):
        pass

    """ retrieve list of type of this class
        @return types [EmType]:
    """
    def types(self):
        records = self._typesDb()
        types = [ EditorialModel.types.EmType(int(record.uid)) for record in records ]

        return types

    def _typesDb(self):
        dbe = self.__class__.getDbE()
        emtype = sql.Table(EditorialModel.types.EmType.table, sqlutils.meta(dbe))
        req = emtype.select().where(emtype.c.class_id == self.id)
        conn = dbe.connect()
        res = conn.execute(req)
        return res.fetchall()

    """ add a new EmType that can ben linked to this class
        @param  t EmType: type to link
        @return success bool: done or not
    """
    def link_type(self, t):
        pass

    """ retrieve list of EmType that are linked to this class
        @return types [EmType]:
    """
    def linked_types(self):
        pass
