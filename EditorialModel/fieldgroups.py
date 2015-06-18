#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.classes import EmClass
import EditorialModel.fieldtypes as ftypes

from Database import sqlutils
import sqlalchemy as sql

import EditorialModel

class EmFieldGroup(EmComponent):
    """ Represents groups of EmField

        EmClass fields representation is organised with EmFieldGroup
        @see EmField
    """

    table = 'em_fieldgroup'
    _fields = [('class_id', ftypes.EmField_integer())]

    def __init__(self, id_or_name):
        """ Instanciate an EmFieldGroup with data fetched from db
            @param id_or_name str|int: Identify the EmFieldGroup by name or by global_id
            @throw TypeError
            @see component::EmComponent::__init__()
        """
        self.table = EmFieldGroup.table
        self._fields = self.__class__._fields
        super(EmFieldGroup, self).__init__(id_or_name)

    @classmethod
    def create(c, name, em_class):
        """ Create a new EmFieldGroup, save it and instanciate it

            @param name str: The name of the new fielgroup
            @param em_class EmClass|str|int: The new EmFieldGroup will belong to this class
        """
        if not isinstance(em_class, EmClass):
            if isinstance(em_class, int) or isinstance(em_class, str):
                try:
                    arg = em_class
                    em_class = EmClass(arg)
                except EmComponentNotExistError:
                    raise ValueError("No EmClass found with id or name '"+arg+"'")
            else:
                raise TypeError("Excepting an EmClass, an int or a str for 'em_class' argument. Not an "+str(type(em_class))+".")

        if not isinstance(name, str):
            raise TypeError("Excepting a string as first argument, not an "+str(type(name)))

        try:
            exists = EmFieldGroup(name)
            raise ValueError("An EmFieldgroup named "+name+" allready exist")
        except EmComponentNotExistError:
            return super(EmFieldGroup, c).create(name=name, class_id = em_class.uid) #Check the return value ?

        return exists

    def fields(self):
        """ Get the list of associated fields
            @return A list of EmField
        """
        pass
