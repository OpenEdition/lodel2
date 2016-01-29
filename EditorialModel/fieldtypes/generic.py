#-*- coding: utf-8 -*-

## @package EditorialModel.fieldtypes.generic Class definition for fieldtypes

import copy
import types
import importlib

## @brief Abstract class for all fieldtypes
class GenericFieldType(object):
    
    help_text = 'Generic field type : abstract class for every fieldtype'
    
    ## @brief List fields that will be exposed to the construct_data_method
    _construct_datas_deps = []

    ## @brief Generic constructor for fieldtypes 
    # @param internal False | str : define wheter or not a field is internal
    # @param immutable bool : indicate if the fieldtype has to be defined in child classes of LeObject or if it is defined globally and immutable
    # @param **args
    # @throw NotImplementedError if called from bad class
    def __init__(self, internal = False, immutable = False, **args):
        if self.__class__ == GenericFieldType:
            raise NotImplementedError("Abstract class")
        self.internal = internal #Check this value ?
        self.immutable = bool(immutable)
    
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
    # @param cur_value : the value for the current field (identified by fieldname)
    # @return constructed datas (for the fname field)
    # @throw RuntimeError if unable to construct data
    def construct_data(self, lec, fname, datas, cur_value):
        if fname in datas.keys():
            return cur_value
        elif hasattr(lec.fieldtypes()[fname], 'default'):
            return lec.fieldtypes()[fname].default
        elif lec.fieldtypes()[fname].nullable:
            return None
        raise RuntimeError("Unable to construct data for field %s", fname)

    ## @brief Check datas consistency
    # @param lec LeCrud : A LeCrud child class instance
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

## @brief Represent fieldtypes handling a single value
class SingleValueFieldType(GenericFieldType):
    
    ## @brief Instanciate a new fieldtype
    # @param nullable bool : is None allowed as value ?
    # @param uniq bool : Indicate if a field should handle uniq value
    # @param primary bool : If True the field is a primary key
    # @param internal str|False : if False the field is not internal. Else can be 'autosql' or 'internal'
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

## @brief Abstract class for fieldtype representing references
#
# In MySQL its foreign keys (for example leo fieldtypes)
class ReferenceFieldType(SingleValueFieldType):

    ## @brief Instanciate a new fieldtype
    #
    #
    # @param reference str : A string that defines the reference (can be 'object' or 'relation')
    # @param nullable bool : is None allowed as value ?
    # @param uniq bool : Indicate if a field should handle uniq value
    # @param primary bool : If True the field is a primary key
    # @param internal str|False : if False the field is not internal. Else can be 'autosql' or 'internal'
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

## @brief Abstract class for fieldtypes handling multiple values identified by a key
#
# For example i18n fieldtype
class MultiValueFieldType(GenericFieldType):
    
    ## @brief Instanciate a new multivalue fieldtype
    #
    # This fieldtype describe a field that handles multiple values referenced by a key (like a dict).
    # A typicall example is the i18n fieldtype
    # @param keyname str : The identifier key name
    # @param key_fieldtype SingleValueFieldType : A SingleValueFieldType child class instance
    # @param value_fieldtype SingleValueFieldType : A SingleValueFieldType child class instance
    # @param internal str|False : if False the field is not internal. Else can be 'autosql' or 'internal'
    # @param **args
    def __init__(self, keyname, key_fieldtype, value_fieldtype, internal = False, **args):
        super().__init__(internal)
        ## stores the keyname
        self.keyname = keyname
        ## stores the fieldtype that handles the key
        self.key_fieldtype = key_fieldtype
        ## stores the fieldtype that handles the values
        self.value_fieldtype = value_fieldtype

## @brief Class designed to handle datas access will fieldtypes are constructing datas
#
# This class is designed to allow automatic scheduling of construct_data calls. 
#
# In theory it's able to detect circular dependencies
# @todo test circular deps detection
# @todo test circulat deps false positiv
class DatasConstructor(object):
    
    ## @brief Init a DatasConstructor
    # @param lec LeCrud : LeCrud child class 
    # @param datas dict : dict with field name as key and field values as value
    # @param fieldtypes dict : dict with field name as key and fieldtype as value
    def __init__(self, lec, datas, fieldtypes):
        ## Stores concerned class
        self._lec = lec
        ## Stores datas and constructed datas
        self._datas = copy.copy(datas)
        ## Stores fieldtypes
        self._fieldtypes = fieldtypes
        ## Stores list of fieldname for constructed datas
        self._constructed = []
        ## Stores construct calls list
        self._construct_calls = []
    
    ## @brief Implements the dict.keys() method on instance
    def keys(self):
        return self._datas.keys()
    
    ## @brief Allows to access the instance like a dict
    def __getitem__(self, fname):
        if fname not in self._constructed:
            if fname in self._construct_calls:
                raise RuntimeError('Probably circular dependencies in fieldtypes')
            cur_value = self._datas[fname] if fname in self._datas else None
            self._datas[fname] = self._fieldtypes[fname].construct_data(self._lec, fname, self, cur_value)
            self._constructed.append(fname)
        return self._datas[fname]
    
    ## @brief Allows to set instance values like a dict
    # @warning Should not append in theory
    def __setitem__(self, fname, value):
        self._datas[fname] = value
        warnings.warn("Setting value of an DatasConstructor instance")
        

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

## @page lodel2_fieldtypes Lodel2 fieldtypes
#
# @section fieldtypes_features Main features
#
# Lodel2 defines Class and Types containing fields that handle values.
# Fields are defined by FieldTypes. It's objects that are able to check datas value, to construct values (~cast) and to check datas consistency given the list of datas of an Lodel2 object (Class or Type)
#
# @subsection fieldtypes_hierarchy Fieldtypes family
#
# Fieldtypes are python objects. We use inheritance to defines FieldTypes. Here is a list of main FieldTypes inheritance :
# - GenericFieldType
#  - SingleValueFieldType <- handles a single value
#   - ReferenceFieldType <- handles a reference to another field
#    - leo.EmFieldType <- handles references to a LeObject (designed for LeRelation)
#   - char.EmFieldType <- handles string
#   - integer.EmFieldType <- handles integer
#    - pk.EmFieldType <- handles primary keys (identifier)
#  - MultiValueFieldType <- handles multiple values identified by a key
#   - i18n.EmFieldType <- handles a string and its translations
#
# @subsection fieldtypes_options Fieldtypes main options
#
# There is 2 options that are common for every fieldtypes :
# - internal : that indicate who construct the data. Possible values are
#  - False : the field is not internal, its user that provides datas
#  - 'automatic' : The field is internal, its leapi that provides datas (see construct in @ref fieldtypes_validator )
#  - 'autosql' : BAD NAME. The field is internal but it is the datasource that provide the data
# - immutable : Its a boolean that indicate if a fieldtype defined in EditorialModel.classtypes is immutable or HAVE TO be defined in EmClass
# 
# @subsubsection fieldtypes_options_single_value SingleValueFieldType options
#
# SingleValueFieldType have more standart options :
# - nullable (boolean) : is None allowed as value
# - uniq (boolean) : if True the value has to be uniq in all instances of concerned Lodel2 API object
# - primary (boolean) : if True the field is an identifier (primary key)
# - default : if given as argument defines a default value for the FieldType
#
# @subsection fieldtypes_validator Data validation
#
# For each Lodel2 API objects (LeObject, LeRelation, ...) there is a sequence that is run to check datas and transform them. Each step is run for each fieldtypes of a Lodel2 API object
#
# -# Check data : this is a basic data check (for example if an integer is expected and the string 'foo' is given the check will fails)
# -# Construct data : this is a data 'casting' step, this method is called with all other datas from the Lodel2 API object as argument (to be able to construct datas with other parts of the object) @ref fieldtypes_construct_order
# -# Datas consistency checks : this step, as the construct step, has all datas from the Lodel2 API object as argument, and check for the whole datas consistency
#
# @subsubsection fieldtypes_construct_order Data construction dependencies
#
# To handle data construction dependencies there is an object DatasConstructor able to call the data construction when needed and to detect (not tested yet) circular dependencies
# 
