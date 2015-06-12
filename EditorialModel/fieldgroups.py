#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Database import sqlutils
import sqlalchemy as sql

import EditorialModel

class EmFieldGroup(EmComponent):
    """ Represents groups of EmField

        EmClass fields representation is organised with EmFieldGroup
        @see EmField
    """

    table = 'em_fieldgroup'

    def __init__(self, id_or_name):
        """ Instanciate an EmFieldGroup with data fetched from db
            @param id_or_name str|int: Identify the EmFieldGroup by name or by global_id
            @throw TypeError
            @see component::EmComponent::__init__()
        """
        self.table = EmFieldGroup.table
        super(EmFieldGroup, self).__init__(id_or_name)

    @classmethod
    def create(c, name, em_class):
        """ Create a new EmFieldGroup, save it and instanciate it

            @param name str: The name of the new fielgroup
            @param em_class EmClass: The new EmFieldGroup will belong to this class
        """
        try:
            exists = EmFieldGroup(name)
        except EmComponentNotExistError:
            return super(EmFieldGroup, c).create({'name': name, 'class_id':em_class.id}) #Check the return value ?

        return exists

    """ Use dictionary (from database) to populate the object
    """
    def populate(self):
        row = super(EmFieldGroup, self).populate()
        self.em_class = EditorialModel.classes.EmClass(int(row.class_id))

    def save(self):
        # should not be here, but cannot see how to do this
        if self.name is None:
            self.populate()

        values = {
            'class_id' : self.em_class.id,
        }

        return super(EmFieldGroup, self).save(values)

    def fields(self):
        """ Get the list of associated fields
            @return A list of EmField
        """
        pass