#-*- coding: utf-8 -*-

import types
import importlib


## @brief Abstract class representing a fieldtype
# 
# Important notes on datas checking :
class GenericFieldType(object):

    ## @brief Text describing the fieldtype
    help = 'Generic field type : abstract class for every fieldtype'
    ## @brief Allowed type for handled datas
    _allowed_ftype = ['char', 'str', 'int', 'bool', 'datetime', 'text', 'rel2type', 'leobject']

    ## @brief The basic lowlevel value type
    ftype = None

    ## @brief Instanciate a new fieldtype
    # @param ftype str : The type of datas handled by this fieldtype
    # @param nullable bool : is None allowed as value ?
    # @param check_function function : A callback check function that takes 1 argument and raise a TypeError if the validation fails
    # @param uniq bool : Indicate if a field should handle uniq values
    # @param primary bool : If true the field is a primary key
    # @param **kwargs dict : Other arguments
    # @throw NotImplementedError if called directly
    # @throw AttributeError if bad ftype
    # @throw AttributeError if bad check_function
    def __init__(self, ftype, nullable=True, check_data_value=None, uniq=False, primary=False, **kwargs):
        if self.__class__ == GenericFieldType:
            raise NotImplementedError("Abstract class")

        if self.ftype is None:
            raise RuntimeError("The class attribute ftype is not properly set by the %s EmFieldType" % self.name)

        if ftype not in self._allowed_ftype:
            raise AttributeError("Ftype '%s' not known" % ftype)

        if ftype != self.__class__.ftype:
            raise RuntimeError("The ftype is not the same for the instance and the class. Maybe %s reimplement ftype at class level but shouldn't" % self.name)

        self.ftype = ftype
        self.nullable = bool(nullable)
        self.uniq = bool(uniq)

        if 'default' in kwargs:
            self.default, error = self.check_data_value(kwargs['default'])
            if error:
                raise error
            del kwargs['default']

        for argname, argvalue in kwargs.items():
            setattr(self, argname, argvalue)

    ## @return A fieldtype name from an instance
    @property
    def name(self):
        return self.__module__.split('.')[-1]
    
    ## @return True if a field is internal, else returns False
    def is_internal(self):
        return hasattr(self, 'internal') and self.internal

    ## @brief Check if a Value is correct else return a check fail reason
    # @param value * : The value to check
    # @return (checked_and_casted_value, Exception|None)
    def check_data_value(self, value):
        if value is None:
            if not self.nullable:
                return (None, TypeError("'None' value but field is not nullable"))
            return (None, None)
        return self._check_data_value(value)
    
    ## @brief Build automatic fields values
    # @param lec LeCrud : A LeCrud child class
    # @param fname str : The field name
    # @param datas dict : dict storing fields values
    # @return constructed datas
    def construct_data(self, lec, fname, datas):
        return datas[fname]
    
    ## @brief Check datas consistency
    # @param leo LeCrud : A LeCrud child class instance
    # @param fname str : The field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    def check_data_consistency(self, lec, fname, datas):
        return True

    ## @brief Dummy check, designed to be implemented in child classes
    # @param value * : The value
    # @return (checked_and_casted_value, Exception|None)
    def _check_data_value(self, value):
        return (value, None)

    ## @brief Given a fieldtype name return the associated python class
    # @param fieldtype_name str : A fieldtype name
    # @return An GenericFieldType derivated class
    @staticmethod
    def from_name(fieldtype_name):
        mod = importlib.import_module(GenericFieldType.module_name(fieldtype_name))
        return mod.EmFieldType

    ## @brief Get a module name given a fieldtype name
    # @param fieldtype_name str : A fieldtype name
    # @return a string representing a python module name
    @staticmethod
    def module_name(fieldtype_name):
        return 'EditorialModel.fieldtypes.%s' % (fieldtype_name)

    ## @brief __hash__ implementation for fieldtypes
    def __hash__(self):
        hash_dats = [self.__class__.__module__]
        for kdic in sorted([k for k in self.__dict__.keys() if not k.startswith('_')]):
            hash_dats.append((kdic, getattr(self, kdic)))
        return hash(tuple(hash_dats))

    ## @brief Transform a value into a valid python representation according to the fieldtype
    # @param value ? : The value to cast
    # @param kwargs dict : optionnal cast arguments
    # @return Something (depending on the fieldtype
    # @throw AttributeError if error in argument given to the method
    # @throw TypeError if the cast is not possible
    def cast(self, value, **kwargs):
        if len(kwargs) > 0:
            raise AttributeError("No optionnal argument allowed for %s cast method" % self.__class__.__name__)
        return value


class FieldTypeError(Exception):
    pass

class FieldTypeDataCheckError(FieldTypeError):

    ## @brief Instanciate a new data check error
    # @param expt_l list : A list of data check Exception
    def __init__(self, expt_l):
        self._expt_l = expt_l

    def __str__(self):
        msg = "Data check errors : "
        for expt in self._expt_l:
            msg += "{expt_name}:{expt_msg}; ".format(expt_name=expt.__class__.__name__, expt_msg=str(expt))
        return msg


