# -*- coding: utf-8 -*-

## @package lodel.leapi.datahandlers.base_classes Define all base/abstract class for data handlers
#
# Contains custom exceptions too

import copy
import importlib
import inspect

from lodel import logger


class FieldValidationError(Exception):
    pass

##@brief Base class for all data handlers
class DataHandler(object):
    
    __HANDLERS_MODULES = ('datas_base', 'datas', 'references')
    ##@brief Stores the DataHandler childs classes indexed by name
    __base_handlers = None
    ##@brief Stores custom datahandlers classes indexed by name
    # @todo do it ! (like plugins, register handlers... blablabla)
    __custom_handlers = dict()

    help_text = 'Generic Field Data Handler'

    ##@brief List fields that will be exposed to the construct_data_method
    _construct_datas_deps = []

    ##@brief constructor
    # @param internal False | str : define whether or not a field is internal
    # @param immutable bool : indicates if the fieldtype has to be defined in child classes of LeObject or if it is
    #                         designed globally and immutable
    # @param **args
    # @throw NotImplementedError if it is instanciated directly
    def __init__(self, **kwargs):
        if self.__class__ == DataHandler:
            raise NotImplementedError("Abstract class")
        
        self.__arguments = kwargs

        self.nullable = True
        self.uniq = False
        self.immutable = False
        self.primary_key = False
        self.internal = False
        if 'defaults' in kwargs:
            self.default, error = self.check_data_value(kwargs['default'])
            if error:
                raise error
            del(args['default'])

        for argname, argval in kwargs.items():
            setattr(self, argname, argval)

    ## Fieldtype name
    @staticmethod
    def name(cls):
        return cls.__module__.split('.')[-1]

    @classmethod
    def is_reference(cls):
        return issubclass(cls, Reference)

    def is_primary_key(self):
        return self.primary_key

    ##@brief checks if a fieldtype is internal
    # @return bool
    def is_internal(self):
        return self.internal is not False

    ##@brief calls the data_field defined _check_data_value() method
    # @return tuple (value, error|None)
    def check_data_value(self, value):
        if value is None:
            if not self.nullable:
                return None, TypeError("'None' value but field is not nullable")

            return None, None
        return self._check_data_value(value)

    ##@brief checks if this class can override the given data handler
    # @param data_handler DataHandler
    # @return bool
    def can_override(self, data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False
        return True

    ##@brief Build field value
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname str : The field name
    # @param datas dict : dict storing fields values (from the component)
    # @param cur_value : the value from the current field (identified by fieldname)
    # @return the value
    # @throw RunTimeError if data construction fails
    def construct_data(self, emcomponent, fname, datas, cur_value):
        emcomponent_fields = emcomponent.fields()
        fname_data_handler = None
        if fname in emcomponent_fields:
            fname_data_handler = DataHandler.from_name(emcomponent_fields[fname])

        if fname in datas.keys():
            return cur_value
        elif fname_data_handler is not None and hasattr(fname_data_handler, 'default'):
                return fname_data_handler.default
        elif fname_data_handler is not None and fname_data_handler.nullable:
                return None

        return RuntimeError("Unable to construct data for field %s", fname)

    ##@brief Check datas consistency
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname : the field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    # @todo A implémenter
    def check_data_consistency(self, emcomponent, fname, datas):
        return True

    ##@brief This method is use by plugins to register new data handlers
    @classmethod
    def register_new_handler(cls, name, data_handler):
        if not inspect.isclass(data_handler):
            raise ValueError("A class was expected but %s given" % type(data_handler))
        if not issubclass(data_handler, DataHandler):
            raise ValueError("A data handler HAS TO be a child class of DataHandler")
        cls.__custom_handlers[name] = data_handler

    @classmethod
    def load_base_handlers(cls):
        if cls.__base_handlers is None:
            cls.__base_handlers = dict()
            for module_name in cls.__HANDLERS_MODULES:
                module = importlib.import_module('lodel.leapi.datahandlers.%s' % module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        logger.debug("Load data handler %s.%s" % (obj.__module__, obj.__name__))
                        cls.__base_handlers[name.lower()] = obj
        return copy.copy(cls.__base_handlers)

    ##@brief given a field type name, returns the associated python class
    # @param fieldtype_name str : A field type name (not case sensitive)
    # @return DataField child class
    # @todo implements custom handlers fetch
    # @note To access custom data handlers it can be cool to preffix the handler name by plugin name for example ? (to ensure name unicity)
    @classmethod
    def from_name(cls, name):
        name = name.lower()
        if name not in cls.__base_handlers:
            raise NameError("No data handlers named '%s'" % (name,))
        return cls.__base_handlers[name]
 
    ##@brief Return the module name to import in order to use the datahandler
    # @param data_handler_name str : Data handler name
    # @return a str
    @classmethod
    def module_name(cls, name):
        name = name.lower()
        handler_class = cls.from_name(name)
        return '{module_name}.{class_name}'.format(
                                                    module_name = handler_class.__module__,
                                                    class_name = handler_class.__name__
        )
            
    ##@brief __hash__ implementation for fieldtypes
    def __hash__(self):
        hash_dats = [self.__class__.__module__]
        for kdic in sorted([k for k in self.__dict__.keys() if not k.startswith('_')]):
            hash_dats.append((kdic, getattr(self, kdic)))
        return hash(tuple(hash_dats))

##@brief Base class for datas data handler (by opposition with references)
class DataField(DataHandler):
    pass

##@brief Abstract class for all references
#
# References are fields that stores a reference to another
# editorial object
class Reference(DataHandler):

    ##@brief Instanciation
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param back_reference tuple | None : tuple containing (LeObject child class, fieldname)
    # @param internal bool : if False, the field is not internal
    # @param **kwargs : other arguments
    def __init__(self, allowed_classes = None, back_reference = None, internal=False, **kwargs):
        self.__allowed_classes = None if allowed_classes is None else set(allowed_classes)
        if back_reference is not None:
            if len(back_reference) != 2:
                raise ValueError("A tuple (classname, fieldname) expected but got '%s'" % back_reference)
            #if not issubclass(back_reference[0], LeObject) or not isinstance(back_reference[1], str):
            #    raise TypeError("Back reference was expected to be a tuple(<class LeObject>, str) but got : (%s, %s)" % (back_reference[0], back_reference[1]))
        self.__back_reference = back_reference
        super().__init__(internal=internal, **kwargs)
    
    @property
    def back_reference(self):
        return copy.copy(self.__back_reference)

    ##@brief Set the back reference for this field.
    def _set_back_reference(self, back_reference):
        self.__back_reference = back_reference
        

    ##@brief Check value
    # @param value *
    # @return tuple(value, exception)
    # @todo implement the check when we have LeObject to check value
    def _check_data_value(self, value):
        return value, None
        if isinstance(value, lodel.editorial_model.components.EmClass):
            value = [value]
        for elt in value:
            if not issubclass(elt.__class__, EmClass):
                return None, FieldValidationError("Some elements of this references are not EmClass instances")
            if self.__allowed_classes is not None:
                if not isinstance(elt, self.__allowed_classes):
                    return None, FieldValidationError("Some element of this references are not valids (don't fit with allowed_classes")
        return value


##@brief This class represent a data_handler for single reference to another object
#
# The fields using this data handlers are like "foreign key" on another object
class SingleRef(Reference):
    
    def __init__(self, allowed_classes = None, **kwargs):
        super().__init__(allowed_classes = allowed_classes)
 
    def _check_data_value(self, value):
        val, expt = super()._check_data_value(value)
        if not isinstance(expt, Exception):
            if len(val) > 1:
               return None, FieldValidationError("Only single values are allowed for SingleRef fields")
        return val, expt


##@brief This class represent a data_handler for multiple references to another object
#
# The fields using this data handlers are like SingleRef but can store multiple references in one field
# @note SQL implementation could be tricky
class MultipleRef(Reference):
    
    ##
    # @param max_item int | None : indicate the maximum number of item referenced by this field, None mean no limit
    def __init__(self, max_item = None, **kwargs):
        super().__init__(**kwargs)

        
    def _check_data_value(self, value):
        if self.max_item is not None:
            if self.max_item < len(value):
                return None, FieldValidationError("To many items")

## @brief Class designed to handle datas access will fieldtypes are constructing datas
#
# This class is designed to allow automatic scheduling of construct_data calls. 
#
# In theory it's able to detect circular dependencies
# @todo test circular deps detection
# @todo test circulat deps false positiv
class DatasConstructor(object):
    
    ## @brief Init a DatasConstructor
    # @param lec LeCrud : @ref LeObject child class 
    # @param datas dict : dict with field name as key and field values as value
    # @param fields_handler dict : dict with field name as key and data handler instance as value
    def __init__(self, leobject, datas, fields_handler):
        ## Stores concerned class
        self._leobject = leobject
        ## Stores datas and constructed datas
        self._datas = copy.copy(datas)
        ## Stores fieldtypes
        self._fields_handler = fields_handler
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
            self._datas[fname] = self._fields_handler[fname].construct_data(self._leobject, fname, self, cur_value)
            self._constructed.append(fname)
        return self._datas[fname]
    
    ## @brief Allows to set instance values like a dict
    # @warning Should not append in theory
    def __setitem__(self, fname, value):
        self._datas[fname] = value
        warnings.warn("Setting value of an DatasConstructor instance")
 
