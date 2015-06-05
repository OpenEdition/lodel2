# -*- coding: utf-8 -*-

""" Manipulate Classes of the Editorial Model
    Create classes of object
    @see EmClass, EmType, EmFieldGroup, EmField
"""

import logging as logger

from EditorialModel.components import EmComponent, EmComponentNotExistError
#from Database.sqlwrapper import SqlWrapper
from Database import sqlutils
import sqlalchemy as sql

import EditorialModel



class EmClass(EmComponent):
    table = 'em_class'

    def __init__(self, id_or_name):
        self.table = EmClass.table
        super(EmClass, self).__init__(id_or_name)

    """ create a new class
        @param name str: name of the new class
        @param class_type EmClasstype: type of the class
    """
    @classmethod
    def create(c, name, class_type):
        try:
            exists = EmClass(name)
            logger.info("Trying to create an EmClass that allready exists")
        except EmComponentNotExistError:
            return c._createDb(name, class_type)

        return exists

    @classmethod
    def _createDb(c, name, class_type):
        """ Do the db querys for EmClass::create() """
        dbe = c.getDbE()
        #Create a new uid
        uids = sql.Table('uids', sqlutils.meta(dbe))
        conn = dbe.connect()
        req = uids.insert(values={'table':c.table})
        res = conn.execute(req)
        
        uid = res.inserted_primary_key

        #Create a new entry in the em_class table
        dbclass = sql.Table(c.table, sqlutils.meta(dbe))
        req = dbclass.insert().values(uid = uid, name=name, classtype=class_type['name'])
        res = conn.execute(req)

        #Create a new table storing LodelObjects of this EmClass
        meta = sql.MetaData()
        emclasstable = sql.Table(name, meta,
            sql.Column('uid', sql.VARCHAR(50), primary_key = True))
        emclasstable.create(conn)

        conn.close()

        return EmClass(res.inserted_primary_key)


    def populate(self):
        row = super(EmClass, self).populate()
        self.classtype = row.classtype
        self.icon = row.icon
        self.sortcolumn = row.sortcolumn

    def save(self):
        # should not be here, but cannot see how to do this
        if self.name is None:
            self.populate()

        values = {
            'classtype' : self.classtype,
            'icon' : self.icon,
            'sortcolumn' : self.sortcolumn,
        }

        return super(EmClass, self).save(values)

    """ retrieve list of the field_groups of this class
        @return field_groups [EmFieldGroup]:
    """
    def fieldgroups(self):
        fieldgroups_req = SqlObject(EditorialModel.fieldgroups.EmFieldGroup.table)
        select = fieldgroups_req.sel
        select.where(fieldgroups_req.col.class_id == self.id)

        sqlresult = fieldgroups_req.rexec(select)
        records = sqlresult.fetchall()
        fieldgroups = [ EditorialModel.fieldgroups.EmFieldGroup(int(record.uid)) for record in records ]

        return fieldgroups

    """ retrieve list of fields
        @return fields [EmField]:
    """
    def fields(self):
        pass

    """ retrieve list of type of this class
        @return types [EmType]:
    """
    def types(self):
        emtype = SqlObject(EditorialModel.types.EmType.table)
        select = emtype.sel
        select.where(emtype.col.class_id == self.id)

        sqlresult = emtype.rexec(select)
        records = sqlresult.fetchall()
        types = [ EditorialModel.types.EmType(int(record.uid)) for record in records ]

        return types

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
