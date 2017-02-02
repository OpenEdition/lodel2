#-*- coding: utf-8 -*-

## @package lodel.leapi.datahandlers.base_classes Define all base/abstract class for data handlers
#
# Contains custom exceptions too

import copy
import importlib
import inspect
import warnings

from lodel.context import LodelContext

LodelContext.expose_modules(globals(), {
    'lodel.exceptions': ['LodelException', 'LodelExceptions',
        'LodelFatalError', 'DataNoneValid', 'FieldValidationError'],
    'lodel.leapi.datahandlers.exceptions': ['LodelDataHandlerConsistencyException', 'LodelDataHandlerException'],
    'lodel.logger': 'logger'})


##@brief Base class for all data handlers
#@ingroup lodel2_datahandlers
class DataHandler(object):
    base_type = "type"
    _HANDLERS_MODULES = ('datas_base', 'datas', 'references')
    ##@brief Stores the DataHandler childs classes indexed by name
    _base_handlers = None
    ##@brief Stores custom datahandlers classes indexed by name
    # @todo do it ! (like plugins, register handlers... blablabla)
    __custom_handlers = dict()

    help_text = 'Generic Field Data Handler'

    ##@brief List fields that will be exposed to the construct_data_method
    _construct_datas_deps = []

    directly_editable = True
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
        if 'default' in kwargs:
            self.default, error = self.check_data_value(kwargs['default'])
            if error:
                raise error
            del(kwargs['default'])
        for argname, argval in kwargs.items():
            setattr(self, argname, argval)

    ## Fieldtype name
    @classmethod
    def name(cls):
        return cls.__module__.split('.')[-1]

    @classmethod
    def is_reference(cls):
        return issubclass(cls, Reference)

    @classmethod
    def is_singlereference(cls):
        return issubclass(cls, SingleRef)

    def is_primary_key(self):
        return self.primary_key

    ##@brief checks if a fieldtype is internal
    # @return bool
    def is_internal(self):
        return self.internal is not False

    ##brief check if a value can be nullable
    #@param value *
    #@throw DataNoneValid if value is None and nullable. LodelExceptions if not nullable
    #@return value (if not None)
    # @return value
    def _check_data_value(self, value):
        if value is None:
            if not self.nullable:
                raise LodelExceptions("None value is forbidden for this data field")
            raise DataNoneValid("None with a nullable. This exeption is allowed")
        return value

    ##@brief calls the data_field (defined in derived class) _check_data_value() method
    #@param value *
    #@return tuple (value|None, None|error) value can be cast if NoneError
    def check_data_value(self, value):
        try:
            value = self._check_data_value(value)
        except DataNoneValid as expt:
            return value, None
        except (LodelExceptions, FieldValidationError) as expt:
            return None, expt
        return value, None

    ##@brief checks if this class can override the given data handler
    # @param data_handler DataHandler
    # @return bool
    def can_override(self, data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False
        return True

    ##@brief Build field value
    #@ingroup lodel2_dh_checks
    #@warning DO NOT REIMPLEMENT THIS METHOD IN A CUSTOM DATAHANDLER (see
    #@ref _construct_data() and @ref lodel2_dh_check_impl )
    #@param emcomponent EmComponent : An EmComponent child class instance
    #@param fname str : The field name
    #@param datas dict : dict storing fields values (from the component)
    #@param cur_value : the value from the current field (identified by fieldname)
    #@return the value
    #@throw RunTimeError if data construction fails
    #@todo raise something else
    def construct_data(self, emcomponent, fname, datas, cur_value):
        emcomponent_fields = emcomponent.fields()
        data_handler = None
        if fname in emcomponent_fields:
            data_handler = emcomponent_fields[fname]
        new_val = cur_value
        if fname in datas.keys():
            pass
        elif data_handler is not None and hasattr(data_handler, 'default'):
            new_val = data_handler.default
        elif data_handler is not None and data_handler.nullable:
            new_val = None
        return self._construct_data(emcomponent, fname, datas, new_val)

    ##@brief Designed to be reimplemented by child classes
    #@param emcomponent EmComponent : An EmComponent child class instance
    #@param fname str : The field name
    #@param datas dict : dict storing fields values (from the component)
    #@param cur_value : the value from the current field (identified by fieldname)
    #@return the value
    #@see construct_data() lodel2_dh_check_impl
    def _construct_data(self, empcomponent, fname, datas, cur_value):
        return cur_value

    ##@brief Check datas consistency
    #@ingroup lodel2_dh_checks
    #@warning DO NOT REIMPLEMENT THIS METHOD IN A CUSTOM DATAHANDLER (see
    #@ref _construct_data() and @ref lodel2_dh_check_impl )
    #@warning the datas argument looks like a dict but is not a dict
    #see @ref base_classes.DatasConstructor "DatasConstructor" and
    #@ref lodel2_dh_datas_construction "Datas construction section"
    #@param emcomponent EmComponent : An EmComponent child class instance
    #@param fname : the field name
    #@param datas dict : dict storing fields values
    #@return an Exception instance if fails else True
    #@todo A implémenter
    def check_data_consistency(self, emcomponent, fname, datas):
        return self._check_data_consistency(emcomponent, fname, datas)

    ##@brief Designed to be reimplemented by child classes
    #@param emcomponent EmComponent : An EmComponent child class instance
    #@param fname : the field name
    #@param datas dict : dict storing fields values
    #@return an Exception instance if fails else True
    #@see check_data_consistency() lodel2_dh_check_impl
    def _check_data_consistency(self, emcomponent, fname, datas):
        return True

    ##@brief make consistency after a query
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname : the field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    # @todo A implémenter
    def make_consistency(self, emcomponent, fname, datas):
        pass

    ##@brief This method is use by plugins to register new data handlers
    @classmethod
    def register_new_handler(cls, name, data_handler):
        if not inspect.isclass(data_handler):
            raise ValueError("A class was expected but %s given" % type(data_handler))
        if not issubclass(data_handler, DataHandler):
            raise ValueError("A data handler HAS TO be a child class of DataHandler")
        cls.__custom_handlers[name] = data_handler

    ##@brief Load all datahandlers
    @classmethod
    def load_base_handlers(cls):
        if cls._base_handlers is None:
            cls._base_handlers = dict()
            for module_name in cls._HANDLERS_MODULES:
                module = importlib.import_module('lodel.leapi.datahandlers.%s' % module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        logger.debug("Load data handler %s.%s" % (obj.__module__, obj.__name__))
                        cls._base_handlers[name.lower()] = obj
        return copy.copy(cls._base_handlers)

    ##@brief given a field type name, returns the associated python class
    # @param fieldtype_name str : A field type name (not case sensitive)
    # @return DataField child class
    # @note To access custom data handlers it can be cool to prefix the handler name by plugin name for example ? (to ensure name unicity)
    @classmethod
    def from_name(cls, name):
        cls.load_base_handlers()
        all_handlers = dict(cls._base_handlers, **cls.__custom_handlers)
        name = name.lower()
        if name not in all_handlers:
            raise NameError("No data handlers named '%s'" % (name,))
        return all_handlers[name]

    ##@brief Return the module name to import in order to use the datahandler
    # @param data_handler_name str : Data handler name
    # @return a str
    @classmethod
    def module_name(cls, name):
        name = name.lower()
        handler_class = cls.from_name(name)
        return '{module_name}.{class_name}'.format(
                                                    module_name=handler_class.__module__,
                                                    class_name=handler_class.__name__
        )

    ##@brief __hash__ implementation for fieldtypes
    def __hash__(self):
        hash_dats = [self.__class__.__module__]
        for kdic in sorted([k for k in self.__dict__.keys() if not k.startswith('_')]):
            hash_dats.append((kdic, getattr(self, kdic)))
        return hash(tuple(hash_dats))

##@brief Base class for datas data handler (by opposition with references)
#@ingroup lodel2_datahandlers
class DataField(DataHandler):
    pass

##@brief Abstract class for all references
#@ingroup lodel2_datahandlers
#
# References are fields that stores a reference to another
# editorial object
#@todo Construct data implementation : transform the data into a LeObject
#instance

class Reference(DataHandler):
    base_type = "ref"

    ##@brief Instanciation
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param back_reference tuple | None : tuple containing (LeObject child class, fieldname)
    # @param internal bool : if False, the field is not internal
    # @param **kwargs : other arguments
    def __init__(self, allowed_classes=None, back_reference=None, internal=False, **kwargs):
        self.__allowed_classes = set() if allowed_classes is None else set(allowed_classes)
        self.allowed_classes = list() if allowed_classes is None else allowed_classes # For now usefull to jinja 2
        if back_reference is not None:
            if len(back_reference) != 2:
                raise ValueError("A tuple (classname, fieldname) expected but got '%s'" % back_reference)
            #if not issubclass(lodel.leapi.leobject.LeObject, back_reference[0]) or not isinstance(back_reference[1], str):
            #    raise TypeError("Back reference was expected to be a tuple(<class LeObject>, str) but got : (%s, %s)" % (back_reference[0], back_reference[1]))
        self.__back_reference = back_reference
        super().__init__(internal=internal, **kwargs)

    ##@brief Method designed to return an empty value for this kind of
    #multipleref
    @classmethod
    def empty(cls):
        return None

    ##@brief Property that takes value of a copy of the back_reference tuple
    @property
    def back_reference(self):
        return copy.copy(self.__back_reference)

    ##@brief Property that takes value of datahandler of the backreference or
    #None
    @property
    def back_ref_datahandler(self):
        if self.__back_reference is None:
            return None
        return self.__back_reference[0].data_handler(self.__back_reference[1])

    @property
    def linked_classes(self):
        return copy.copy(self.__allowed_classes)

    ##@brief Set the back reference for this field.
    def _set_back_reference(self, back_reference):
        self.__back_reference = back_reference

    ##@brief Check and cast value in appropriate type
    #@param value *
    #@throw FieldValidationError if value is an appropriate type
    #@return value
    #@todo implement the check when we have LeObject uid check value
    def _check_data_value(self, value):
        from lodel.leapi.leobject import LeObject
        value = super()._check_data_value(value)
        if not (hasattr(value, '__class__') and
                issubclass(value.__class__, LeObject)):
            if self.__allowed_classes:
                rcls = list(self.__allowed_classes)[0]
                uidname = rcls.uid_fieldname()[0]# TODO multiple uid is broken
                uiddh = rcls.data_handler(uidname)
                value = uiddh._check_data_value(value)
            else:
                raise FieldValidationError("Reference datahandler can not check this value %s if any allowed_class is allowed." % value)
        return value

    ##@brief Check datas consistency
    #@param emcomponent EmComponent : An EmComponent child class instance
    #@param fname : the field name
    #@param datas dict : dict storing fields values
    #@return an Exception instance if fails else True
    #@todo check for performance issue and check logics
    #@warning composed uid capabilities broken here
    def check_data_consistency(self, emcomponent, fname, datas):
        rep = super().check_data_consistency(emcomponent, fname, datas)
        if isinstance(rep, Exception):
            return rep
        if self.back_reference is None:
            return True
        # !! Reimplement instance fetching in construct data !!
        target_class = self.back_reference[0]
        if target_class not in self.__allowed_classes:
            logger.warning('Class of the back_reference given is not an allowed class')
            return False
        value = datas[fname]
        if not target_class.is_exist(value):
            logger.warning('Object referenced does not exist')
            return False
        #target_uidfield = target_class.uid_fieldname()[0] #multi uid broken here
        #obj = target_class.get([(target_uidfield, '=', value)])
        #if len(obj) == 0:
        #    logger.warning('Object referenced does not exist')
        #    return False
        return True
    
    ##@brief Utility method designed to fetch referenced objects
    #@param value mixed : the field value
    #@throw NotImplementedError
    def get_referenced(self, value):
        raise NotImplementedError


##@brief This class represent a data_handler for single reference to another object
#
# The fields using this data handlers are like "foreign key" on another object
class SingleRef(Reference):

    def __init__(self, allowed_classes=None, **kwargs):
        super().__init__(allowed_classes=allowed_classes, **kwargs)


    ##@brief Check and cast value in appropriate type
    #@param value: *
    #@throw FieldValidationError if value is unappropriate or can not be cast
    #@return value
    def _check_data_value(self, value):
        value = super()._check_data_value(value)
        return value

    ##@brief Utility method designed to fetch referenced objects
    #@param value mixed : the field value
    #@return A LeObject child class instance
    #@throw LodelDataHandlerConsistencyException if no referenced object found
    def get_referenced(self, value):
        for leo_cls in self.linked_classes:
            res = leo_cls.get_from_uid(value)
            if res is not None:
                return res
        raise LodelDataHandlerConsistencyException("Unable to find \
referenced object with uid %s" % value)


##@brief This class represent a data_handler for multiple references to another object
#@ingroup lodel2_datahandlers
#
# The fields using this data handlers are like SingleRef but can store multiple references in one field
# @note for the moment split on ',' chars
class MultipleRef(Reference):

    ##
    # @param max_item int | None : indicate the maximum number of item referenced by this field, None mean no limit
    def __init__(self, max_item=None, **kwargs):
        self.max_item = max_item
        super().__init__(**kwargs)

    ##@brief Method designed to return an empty value for this kind of
    #multipleref
    @classmethod
    def empty(cls):
        return []

    ##@brief Check and cast value in appropriate type
    #@param value *
    #@throw FieldValidationError if value is unappropriate or can not be cast
    #@return value
    #@TODO  Writing test error for errors when stored multiple references in one field
    def _check_data_value(self, value):
        value = DataHandler._check_data_value(self, value)
        if not hasattr(value, '__iter__'):
            raise FieldValidationError("MultipleRef has to be an iterable or a string, '%s' found" % value)
        if self.max_item is not None:
            if self.max_item < len(value):
                raise FieldValidationError("Too many items")
        new_val = list() 
        error_list = list()
        for i, v in enumerate(value):
            try:
                v = super()._check_data_value(v)
                new_val.append(v)
            except (FieldValidationError):
                error_list.append(repr(v))
        if len(error_list) > 0:
            raise FieldValidationError("MultipleRef have for invalid values [%s]  :" % (",".join(error_list)))
        return new_val

    ##@brief Utility method designed to fetch referenced objects
    #@param values mixed : the field values
    #@return A list of LeObject child class instance
    #@throw LodelDataHandlerConsistencyException if some referenced objects
    #were not found
    def get_referenced(self, values):
        if values is None or len(values) == 0:
            return list()
        left = set(values)
        values = set(values)
        res = list()
        for leo_cls in self.linked_classes:
            uidname = leo_cls.uid_fieldname()[0] #MULTIPLE UID BROKEN HERE
            tmp_res = leo_cls.get(('%s in (%s)' % (uidname, ','.join(
                [str(l) for l in left]))))
            left ^= set(( leo.uid() for leo in tmp_res))
            res += tmp_res
            if len(left) == 0:
                return res
        raise LodelDataHandlerConsistencyException("Unable to find \
some referenced objects. Following uids were not found : %s" % ','.join(left))

## @brief Class designed to handle datas access will fieldtypes are constructing datas
#@ingroup lodel2_datahandlers
#
# This class is designed to allow automatic scheduling of construct_data calls.
#
# In theory it's able to detect circular dependencies
# @todo test circular deps detection
# @todo test circular deps false positive
class DatasConstructor(object):

    ## @brief Init a DatasConstructor
    # @param leobject LeCrud : @ref LeObject child class
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


## @brief Class designed to handle an option of a DataHandler
class DatahandlerOption(object):

    ## @brief instanciates a new Datahandler option object
    #
    # @param id str
    # @param display_name MlString
    # @param help_text MlString
    # @param validator function
    def __init__(self, id, display_name, help_text, validator):
        self.__id = id
        self.__display_name = display_name
        self.__help_text = help_text
        self.__validator = validator

    @property
    def id(self):
        return self.__id

    @property
    def display_name(self):
        return self.__display_name

    @property
    def help_text(self):
        return self.__help_text

    ## @brief checks a value corresponding to this option is valid
    # @param value
    # @return casted value
    def check_value(self, value):
        return self.__validator(value)
