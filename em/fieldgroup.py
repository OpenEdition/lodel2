#-*- coding: utf-8 -*-

from component import EmComponent


class EmFieldGroup(EmComponent):
    """ Represents groups of EmField
            
        EmClass fields representation is organised with EmFieldGroup
        @see EmField
    """
    

    def __init__(id_or_name):
        """ Instanciate an EmFieldGroupe with data fetched from db
            @param id_or_name str|int: Identify the EmFieldGroup by name or by global_id
            @throw TypeError
            @see component::EmComponent::__init__()
        """
        super(EmFieldGroup, self).__init__()
        pass

    @staticmethod
    def create(name, em_class, ml_repr = None, ml_help = None, icon = None):
        """ Create a new EmType and instanciate it
            
            @todo Change the icon param type
            @todo em_class == None => Error ?
            @todo change staticmethod to classmethod ?
            
            @param name str: The name of the new Type
            @param em_class EmClass: The new EmFieldGroup will belong to this class
            @param ml_repr MlString|None: Multilingual representation of the type
            @param ml_help MlString|None: Multilingual help for the type
            @param The string|None: filename of the icon
            @return An EmFieldGroup instance
            @see EmComponent::__init__()
        """
        pass

    def fields():
        """ Get the list of associated fields
            @return A list of EmField
        """
        pass

    def field():
        """ ???
            @todo : find what this function is for
        """
        pass

