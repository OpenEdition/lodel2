#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Database import sqlutils
import sqlalchemy as sql

import EditorialModel.fieldtypes as ftypes
import EditorialModel.classes

class EmType(EmComponent):
    """ Represents type of documents

        A type is a specialisation of a class, it can select optional field,
        they have hooks, are organized in hierarchy and linked to other
        EmType with special fields called relation_to_type fields
        @see EmComponent
    """
    table = 'em_type'

    ## @brief Specific EmClass fields
    # @see EditorialModel::components::EmComponent::_fields
    _fields = [
        ('class_id', ftypes.EmField_integer),
        ('icon', ftypes.EmField_integer),
        ('sortcolumn', ftypes.EmField_char)
        ]

    @classmethod
    def create(c, name, em_class):
        """ Create a new EmType and instanciate it

            @param name str: The name of the new type
            @param em_class EmClass: The class that the new type will specialize

            @see EmComponent::__init__()

            @todo Remove hardcoded default value for icon
            @todo check that em_class is an EmClass object
        """
        try:
            exists = EmType(name)
        except EmComponentNotExistError:
            return super(EmType, c).create(name=name, class_id=em_class.uid, icon=0)

        return exists

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
