#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Database import sqlutils
import sqlalchemy as sql

import EditorialModel.classes

class EmType(EmComponent):
    """ Represents type of documents

        A type is a specialisation of a class, it can select optional field,
        they have hooks, are organized in hierarchy and linked to other
        EmType with special fields called relation_to_type fields
        @see EmComponent
    """
    table = 'em_type'

    def __init__(self, id_or_name):
        """  Instanciate an EmType with data fetched from db
            @param id_or_name str|int: Identify the EmType by name or by global_id
            @throw TypeError
            @see EmComponent::__init__()
        """
        self.table = EmType.table
        super(EmType, self).__init__(id_or_name)

    @staticmethod
    def create(name, em_class):
        """ Create a new EmType and instanciate it

            @param name str: The name of the new type
            @param em_class EmClass: The class that the new type will specialize

            @see EmComponent::__init__()

            @todo Change the icon param type
            @todo change staticmethod to classmethod
        """
        try:
            exists = EmType(name)
        except EmComponentNotExistError:
            return EmType._createDb(name, em_class)

        return exists

    @classmethod
    def _createDb(c, name, em_class):
        uid = c.newUid()

        dbe = c.getDbE()
        conn = dbe.connect()

        #Insert type in db
        dbtype = sql.Table(c.table, sqlutils.meta(dbe))
        req = dbtype.insert().values(uid=uid, name=name, class_id=em_class.id)
        res = conn.execute(req)

        return EmType(name)

    """ Use dictionary (from database) to populate the object
    """
    def populate(self):
        row = super(EmType, self).populate()
        self.em_class = EditorialModel.classes.EmClass(int(row.class_id))
        self.icon = row.icon
        self.sortcolumn = row.sortcolumn

    def save(self):
        # should not be here, but cannot see how to do this
        if self.name is None:
            self.populate()

        values = {
            'class_id' : self.em_class.id,
            'icon' : self.icon,
            'sortcolumn' : self.sortcolumn,
        }

        return super(EmType, self).save(values)

    def field_groups(self):
        """ Get the list of associated fieldgroups
            @return A list of EmFieldGroup
        """
        pass


    def fields(self):
        """ Get the list of associated fields
            @return A list of EmField
        """
        pass

    def select_field(self, field):
        """ Indicate that an optionnal field is used

            @param field EmField: The optional field to select
            @throw ValueError, TypeError
            @todo change exception type and define return value and raise condition
        """
        pass

    def unselect_field(self, field):
        """ Indicate that an optionnal field will not be used
            @param field EmField: The optional field to unselect
            @throw ValueError, TypeError
            @todo change exception type and define return value and raise condition
        """
        pass


    def hooks(self):
        """Get the list of associated hooks"""
        pass

    def add_hook(self, hook):
        """ Add a new hook
            @param hook EmHook: A EmHook instance
            @throw TypeError
        """
        pass

    def del_hook(hook):
        """ Delete a hook
            @param hook EmHook: A EmHook instance
            @throw TypeError
            @todo Maybe we don't need a EmHook instance but just a hook identifier
        """
        pass


    def superiors(self):
        """ Get the list of superiors EmType in the type hierarchy
            @return A list of EmType
        """
        pass


    def add_superior(self, em_type, relation_nature):
        """ Add a superior in the type hierarchy

            @param em_type EmType: An EmType instance
            @param relation_nature str: The name of the relation's nature
            @throw TypeError
            @todo define return value and raise condition
        """
        pass

    def del_superior(self, em_type):
        """ Delete a superior in the type hierarchy

            @param em_type EmType: An EmType instance
            @throw TypeError
            @todo define return value and raise condition
        """
        pass

    def linked_types(self):
        """ Get the list of linked type

            Types are linked with special fields called relation_to_type fields

            @return a list of EmType
            @see EmFields
        """
        pass
