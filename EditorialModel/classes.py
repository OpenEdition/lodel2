# -*- coding: utf-8 -*-

""" Manipulate Classes of the Editorial Model
    Create classes of object
    @see EmClass, EmType, EmFieldGroup, EmField
"""

from EditorialModel.components import EmComponent, EmComponentNotExistError
import EditorialModel.classtypes
from Database.sqlwrapper import SqlWrapper
from Database.sqlobject import SqlObject

class EmClass(EmComponent):
    table = 'em_class'
    def __init__(self, id_or_name):
        self.table = EmClass.table
        super(EmClass, self).__init__(id_or_name)

    """ create a new class
        @param name str: name of the new class
        @param class_type EmClasstype: type of the class
    """
    @staticmethod
    def create(name, class_type):
        try:
            exists = EmClass(name)
        except EmComponentNotExistError:
            uids = SqlObject('uids')
            res = uids.wexec(uids.table.insert().values(table=EmClass.table))
            uid = res.inserted_primary_key

            emclass = SqlObject(EmClass.table)
            res = emclass.wexec(emclass.table.insert().values(uid=uid, name=name, classtype=class_type['name']))
            SqlWrapper.wc().execute("CREATE TABLE %s (uid VARCHAR(50))" % name)
            return EmClass(name)

        return False

    def populate(self):
        row = super(EmClass, self).populate()
        self.classtype = row.classtype
        self.icon = row.icon
        self.sortcolumn = row.sortcolumn

    def save(self):
        # should not be here, but cannot see how to do this
        if self.id is None:
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
    def field_groups():
        pass

    """ retrieve list of fields
        @return fields [EmField]:
    """
    def fields():
        pass

    """ retrieve list of type of this class
        @return types [EmType]:
    """
    def types():
        pass

    """ add a new EmType that can ben linked to this class
        @param  t EmType: type to link
        @return success bool: done or not
    """
    def link_type(t):
        pass

    """ retrieve list of EmType that are linked to this class
        @return types [EmType]:
    """
    def linked_types():
        pass
