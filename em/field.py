#-*- coding: utf-8 -*-

from component import EmComponent

"""Represent one data for a lodel2 document"""
class EmField(EmComponent):

    
    def __init__(id_or_name):
        """ Instanciate an EmType with data fetched from db
            @param id_or_name str|int: Identify the EmType by name or by global_id
            @throw TypeError
            @see EmComponent::__init__()
        """
        super(EmField, self).__init__()
        pass

    def create( name, em_fieldgroup, ml_repr = None, ml_help = None,
                icon = None, optionnal = False, type_relation = None,
                relationnal_field = None, primary_data = False,
                default_value = None, params = None, value = None):
        """ Create a new EmType and instanciate it
            
            @todo Change the icon param type
            @todo change staticmethod to classmethod ?
            @todo simplify function aguments ?
            @todo typeof default_value argument ?
            @todo typeof params argument ?
            @todo typeof value argument ?
            
            @static
            
            @param name str: The name of the new Type
            @param em_fieldgroup EmFieldGroup: The new field will belong to this fieldgroup
            @param ml_repr MlString|None: Multilingual representation of the type
            @param ml_help MlString|None: Multilingual help for the type
            @param The string|None: filename of the icon
            
            @param optionnal bool: Is the field optionnal ?
            @param type_relation EmType|None: If not None make a link between the class of the new EmField and this EmType
            @param relationnal_field EmField|None: If not None indicates that the new field defines the relation created by this EmField argument
            @param primary_data bool: Is the new field a primary data field ?
            @param The default_value: field's default value
            @param Params params: of the field
            @param Value value: of the field
            
            @throw TypeError
            @see EmComponent::__init__()
            @staticmethod
        """
        pass

    def set_default(default_value):
        """ Set the default value
            @todo argument type ?
            @todo return type ?
            @param default_value anytype: The default value
        """
        pass

    def set_param(params):
        """ Set the field parameters
            @todo argument type ? EmFieldParam ?
            @todo return type ?
            @param params anytype: The field parameters
        """
        pass

    def set_value(v):
        """ Set the field value
            
            @todo Better explanations
            
            Don't set the field value in a document, it's a special kind of value
            
            @param The v: value
        """
        pass
