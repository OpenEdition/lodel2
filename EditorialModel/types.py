#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent

class EmType(EmComponent):
    """ Represents type of documents

        A type is a specialisation of a class, it can select optional field,
        they have hooks, are organized in hierarchy and linked to other
        EmType with special fields called relation_to_type fields
        @see EmComponent
    """

    def __init__(id_or_name):
        """  Instanciate an EmType with data fetched from db
            @param id_or_name str|int: Identify the EmType by name or by global_id
            @throw TypeError
            @see EmComponent::__init__()
        """
        super(EmType, self).__init__()
        pass

    @staticmethod
    def create(name, em_class, ml_repr = None, ml_help = None, icon = None, sort_field = None):
        """ Create a new EmType and instanciate it

            @param name str: The name of the new type
            @param em_class EmClass: The class that the new type will specialize
            @param ml_repr MlString: Multilingual representation of the type
            @param ml_help MlString: Multilingual help for the type
            @param icon str|None: The filename of the icon
            @param sort_field EmField|None: The field used to sort by default

            @see EmComponent::__init__()

            @todo Change the icon param type
            @todo change staticmethod to classmethod
        """
        pass

    def field_groups():
        """ Get the list of associated fieldgroups
            @return A list of EmFieldGroup
        """
        pass


    def fields():
        """ Get the list of associated fields
            @return A list of EmField
        """
        pass

    def select_field(field):
        """ Indicate that an optionnal field is used

            @param field EmField: The optional field to select
            @throw ValueError, TypeError
            @todo change exception type and define return value and raise condition
        """
        pass

    def unselect_field(field):
        """ Indicate that an optionnal field will not be used
            @param field EmField: The optional field to unselect
            @throw ValueError, TypeError
            @todo change exception type and define return value and raise condition
        """
        pass

        
    def hooks():
        """Get the list of associated hooks"""
        pass

    def add_hook(hook):
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


    def superiors():
        """ Get the list of superiors EmType in the type hierarchy
            @return A list of EmType
        """
        pass


    def add_superior(em_type, relation_nature):
        """ Add a superior in the type hierarchy
            
            @param em_type EmType: An EmType instance
            @param relation_nature str: The name of the relation's nature
            @throw TypeError
            @todo define return value and raise condition
        """
        pass

    def del_superior(em_type):
        """ Delete a superior in the type hierarchy
            
            @param em_type EmType: An EmType instance
            @throw TypeError
            @todo define return value and raise condition
        """
        pass

    def linked_types():
        """ Get the list of linked type
            
            Types are linked with special fields called relation_to_type fields
            
            @return a list of EmType
            @see EmFields
        """
        pass

