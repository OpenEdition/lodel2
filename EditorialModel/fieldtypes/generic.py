#-*- coding: utf-8 -*-

import types
import importlib

class GenericFieldType(object):
    
    help_text = 'Generic field type : abstract class for every fieldtype'

    ## @param internal False | str : define wheter or not a field is internal
    # @throw NotImplementedError if called from bad class
    def __init__(self, internal = False, **args):
        if self.__class__ == GenericFieldType:
            raise NotImplementedError("Abstract class")
        self.internal = internal #Check this value ?
    
        for argname, argval in args.items():
            setattr(self, argname, argval)
    
    ## Fieldtype name
    # @todo should be a staticmethod
    @property
    def name(self):
        return self.__module__.split('.')[-1]
    
    ## @return True if a fieldtype is internal
    def is_internal(self):
        return self.internal != False
    
    ## @brief Take care to call the fieldtype defined _check_data_value() method
    # @return a tuple (value, error|None)
    def check_data_value(self, value):
        return self._check_data_value(value)

    def _check_data_value(self, value):
        return (value, None)
    
    ## @brief Build field value
    # @param lec LeCrud : A LeCrud child class
    # @param fname str : The field name
    # @param datas dict : dict storing fields values (from the lec)
    # @return constructed datas (for the fname field)
    # @throw RuntimeError if unable to construct data
    def construct_data(self, lec, fname, datas):
        if fname in datas:
            return datas[fname]
        elif hasattr(lec.fieldtypes()[fname], 'default'):
            return lec.fieldtypes()[fname].default
        elif lec.fieldtypes()[fname].nullable:
            return None
        raise RuntimeError("Unable to construct data for field %s", fname)

    ## @brief Check datas consistency
    # @param leo LeCrud : A LeCrud child class instance
    # @param fname str : The field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    def check_data_consistency(self, lec, fname, datas):
        return True

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

class SingleValueFieldType(GenericFieldType):
    
    ## @brief Instanciate a new fieldtype
    # @param nullable bool : is None allowed as value ?
    # @param uniqu bool : Indicate if a field should handle uniq value
    # @param primary bool : If True the field is a primary key
    # @param **args : Other arguments
    # @throw NotImplementedError if called from bad class
    def __init__(self, internal = False, nullable = True, uniq = False, primary = False, **args):
        if self.__class__ == SingleValueFieldType:
            raise NotImplementedError("Asbtract class")

        super().__init__(internal, **args)

        self.nullable = nullable
        self.uniq = uniq
        self.primary = primary
        if 'default' in args:
            self.default, error = self.check_data_value(args['default'])
            if error:
                raise error
            del(args['default'])

    def check_data_value(self, value):
        if value is None:
            if not self.nullable:
                return (None, TypeError("'None' value but field is not nullable"))
            return (None, None)
        return super().check_data_value(value)

class ReferenceFieldType(SingleValueFieldType):

    ## @brief Instanciate a new fieldtype
    #
    #
    # @param reference str : A string that defines the reference (can be 'object' or 'relation')
    # @param nullable bool : is None allowed as value ?
    # @param unique bool : Indicate if a field should handle uniq value
    # @param primary bool : If True the field is a primary key
    # @param **args : Other arguments
    # @throw NotImplementedError if called from bad class
    def __init__(self, reference, internal=False, nullable = True, uniq = False, primary = False, **args):
        if reference.lower() not in ['relation', 'object']:
            raise ValueError("Bad value for reference : %s. Excepted on of 'relation', 'object'" % reference)
        self.reference = reference.lower()
        super().__init__(
                            internal = internal,
                            nullable = nullable,
                            uniq = uniq,
                            primary = primary,
                            **args
        );
        pass

class MultiValueFieldType(GenericFieldType):
    
    ## @brief Instanciate a new multivalue fieldtype
    #
    # This fieldtype describe a field that handles multiple values referenced by a key (like a dict).
    # A typicall example is the i18n fieldtype
    # @param keyname str : The identifier key name
    # @param key_fieldtype SingleValueFieldType : A SingleValueFieldType child class instance
    # @param value_fieldtype SingleValueFieldType : A SingleValueFieldType child class instance
    def __init__(self, internal, keyname, key_fieldtype, value_fieldtype, **args):
        super().__init__(internal)
        ## stores the keyname
        self.keyname = keyname
        ## stores the fieldtype that handles the key
        self.key_fieldtype = key_fieldtype
        ## stores the fieldtype that handles the values
        self.value_fieldtype = value_fieldtype

#
#
#   Exceptions
#
#
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


