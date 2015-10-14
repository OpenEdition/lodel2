#-*- coding: utf-8 -*-

import types

## @brief Abstract class representing a fieldtype
class GenericFieldType(object):
    
    ## @brief Text describing the fieldtype
    help = 'Generic field type : abstract class for every fieldtype'
    ## @brief Allowed type for handled datas
    _allowed_ftype = ['char', 'str', 'int', 'bool', 'datetime', 'text', 'rel2type']
    
    ## @brief Instanciate a new fieldtype
    # @param ftype str : The type of datas handled by this fieldtype
    # @param default ? : The default value
    # @param nullable bool : is None allowed as value ?
    # @param check_function function : A callback check function that takes 1 argument and raise a TypeError if the validation fails
    # @param **kwargs dict : Other arguments
    # @throw NotImplementedError if called directly
    # @throw AttributeError if bad ftype
    # @throw AttributeError if bad check_function
    def __init__(self, ftype, default = None, nullable = False, check_function = None, **kwargs):
        if self.__class__ == GenericFieldType:
            raise NotImplementedError("Abstract class")
        
        if ftype not in self._allowed_ftype:
            raise AttributeError("Ftype '%s' not known"%ftype)
        
        if check_function is None:
            check_function = self.dummy_check
        elif not isinstance(check_function, types.FunctionType):
            raise AttributeError("check_function argument has to be a function")

        self.ftype = ftype
        self.check_function = check_function
        self.nullalble = bool(nullable)

        self.check_or_raise(default)
        self.default = default

        for argname,argvalue in kwargs.items():
            setattr(self, argname, argvalue)
    
    ## @brief Check if a value is correct
    # @param value * : The value
    # @throw TypeError if not valid
    @staticmethod
    def dummy_check(value):
        pass
    
    ## @brief Transform a value into a valid python representation according to the fieldtype
    # @param value ? : The value to cast
    # @param kwargs dict : optionnal cast arguments
    # @return Something (depending on the fieldtype
    # @throw AttributeError if error in argument given to the method
    # @throw TypeError if the cast is not possible
    def cast(self, value, **kwargs):
        if len(kwargs) > 0:
            raise AttributeError("No optionnal argument allowed for %s cast method"%self.__class__.__name__)
        return value
    
    ## @brief Check if a value is correct
    # @param value * : The value to check
    # @return True if valid else False
    def check(self, value):
        try:
            self.check_or_raise(value)
        except TypeError as e:
            return False
        return True

    ## @brief Check if a value is correct
    # @param value * : The value
    # @throw TypeError if not valid
    def check_or_raise(self, value):
        if value is None and not self.nullable:
            raise TypeError("Not nullable field")
        self.check_function(value)

class FieldTypeError(Exception):
    pass

