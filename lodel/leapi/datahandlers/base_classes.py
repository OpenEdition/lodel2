#-*- coding: utf-8 -*-
##
#  @package lodel.leapi.datahandlers.base_classes Defines all base/abstract
#            classes for DataHandlers
#
# Contains custom exceptions too

import copy
import importlib
import inspect
import warnings

from lodel.context import LodelContext

LodelContext.expose_modules(globals(), {
    'lodel.exceptions': [
        'LodelException',
        'LodelExceptions',
        'LodelFatalError',
        'DataNoneValid',
        'FieldValidationError'
    ],
    'lodel.mlnamedobject.mlnamedobject': ['MlNamedObject'],
    'lodel.leapi.datahandlers.exceptions': [
        'LodelDataHandlerConsistencyException',
        'LodelDataHandlerException'
    ],
    'lodel.validator.validator': [
        'ValidationError'
    ],
    'lodel.logger': 'logger',
    'lodel.utils.mlstring': ['MlString']})

##
# @brief Base class for all DataHandlers
# @ingroup lodel2_datahandlers
#
# @remarks Some of the methods and properties in this "abstract" class are 
#            bounded to its children. This implies that the parent
#            is aware of its children, which is an absolute anti-pattern
#            (Liskov / OC violation), a source of confusion and a decrased
#            maintainability. Aggregation =/= Inheritance
#            Concerned methods are: is_reference; is_singlereference.
#            Concerned properties are __custom_datahandlers; base_handlers.
# @remarks What is the purpose of an internal property being set to a 
#            string (namely 'automatic')
# @remarks Two sets of methods appears a little strange in regards to their
#            visibility.
#            - @ref _construct_data / @ref construct_data
#            - @ref _check_data_consistency / @ref check_data_consistency
class DataHandler(MlNamedObject):
    base_type = "type"
    _HANDLERS_MODULES = ('datas_base', 'datas', 'references')
    
    ##
    # @brief Stores the DataHandler child classes indexed by name
    _base_handlers = None
    
    ##
    # @brief Stores custom DataHandlers classes indexed by name
    # @todo do it ! (like plugins, register handlers... blablabla)
    __custom_handlers = dict()

    help_text = 'Generic Field Data Handler'
    display_name = "Generic Field"
    options_spec = dict()
    options_values = dict()

    ##
    # @brief Lists fields that will be exposed to the construct_data method
    _construct_datas_deps = []

    directly_editable = True


    ##
    # @brief constructor
    #
    # @param internal False | str : define whether or not a field is internal
    # @param immutable bool : Indicates if the fieldtype has to be defined in child classes of
    #                         LeObject or if it is designed globally and immutable
    # @throw NotImplementedError If it is instantiated directly
    # @remarks Shouldn't the class be declared abstract? No need to check if it
    #            is instantiated directly, no exception to throw, cleaner code.
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
            del kwargs['default']
        for argname, argval in kwargs.items():
            setattr(self, argname, argval)
        self.check_options()

        display_name = kwargs.get('display_name', MlString(self.display_name))
        help_text = kwargs.get('help_text', MlString(self.help_text))
        super().__init__(display_name, help_text)


    ##
    # @brief Sets properly cast and checked options for the DataHandler
    #
    # @throw LodelDataHandlerNotAllowedOptionException when a passed option 
    #            is not in the option specifications of the DataHandler
    def check_options(self):
        for option_name, option_datas in self.options_spec.items():
            if option_name in self.options_values:
                # There is a configured option, we check its value
                try:
                    self.options_values[option_name] = option_datas[1].check_value(
                        self.options_values[option_name])
                except ValueError:
                    pass  # TODO Deal with the case where the value used for an option is invalid
            else:
                # This option was not configured, we get the default value from the specs
                self.options_values[option_name] = option_datas[0]


    ##
    # @return string: Field type name
    @classmethod
    def name(cls):
        return cls.__module__.split('.')[-1]


    ##
    # @return bool: True if subclass is of Reference type, False otherwise.
    @classmethod
    def is_reference(cls):
        return issubclass(cls, Reference)


    ##
    # @return bool: True if subclass is of SingleRef type, False otherwise.
    @classmethod
    def is_singlereference(cls):
        return issubclass(cls, SingleRef)


    ##
    # @return bool: True if the field is a primary_key, False otherwise.
    def is_primary_key(self):
        return self.primary_key


    ##
    # @brief checks if a field type is internal
    # @return bool: True if the field is internal, False otherwise.
    def is_internal(self):
        return self.internal is not False


    ##
    # @brief check if a value can be nullable
    # 
    # @param value *
    # @throw DataNoneValid if value is None and nullable.
    # @throw LodelExceptions if not nullable
    # @return value (if not None)
    # @return value
    #
    # @remarks why are there an thrown exception if it is allowed?
    #            Exceptions are no message brokers
    def _check_data_value(self, value):
        if value is None:
            if not self.nullable:
                raise LodelExceptions("None value is forbidden for this data field")
            raise DataNoneValid("None with a nullable. This exception is allowed")
        return value


    ##
    # @brief calls the data_field (defined in derived class) _check_data_value() method
    # @param value *
    # @return tuple (value|None, None|error) value can be cast if NoneError
    # @remarks Consider renaming this method, such as '_is_data_nullable'.
    # @remarks Exceptions ARE NOT message brokers! Moreover, those two methods
    #            are more complicated than required. In case 'value' is None,
    #            the returned value is the same as the input value. This is the
    #            same behavior as when the value is not None!
    # @return What's a "NoneError"? Value can be cast to what?
    def check_data_value(self, value):
        try:
            value = self._check_data_value(value)
        except DataNoneValid as expt:
            return value, None
        except (LodelExceptions, FieldValidationError) as expt:
            return None, expt
        return value, None

    ##
    # @brief Checks if this class can override the given data handler.
    #        i.e. both class having the same base_type.  
    # @param data_handler DataHandler
    # @return bool
    # @remarks Simplify by "return data_handler.__class__.base_type == self.__class__.base_type"?
    def can_override(self, data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False
        return True


    ##
    # @brief Build field value
    #
    # @ingroup lodel2_dh_checks
    # @ref _construct_data() and @ref lodel2_dh_check_impl )
    #
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname str : The field name
    # @param datas dict : dict storing fields values (from the component)
    # @param cur_value : the value from the current field (identified by fieldname)
    # @return the value
    # @throw RunTimeError if data construction fails
    #
    # @warning DO NOT REIMPLEMENT THIS METHOD IN A CUSTOM DATAHANDLER (see
    # @todo raise something else
    #
    # @remarks What the todo up right here means? Raise what? When?
    # @remarks Nothing is being raised in this method, should it?
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


    ##
    # @brief Designed to be reimplemented by child classes
    #
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname str : The field name
    # @param datas dict : dict storing fields values (from the component)
    # @param cur_value : the value from the current field (identified by fieldname)
    # @return the value
    # @see construct_data() lodel2_dh_check_impl
    def _construct_data(self, emcomponent, fname, datas, cur_value):
        return cur_value


    ##
    # @brief Check data consistency
    # @ingroup lodel2_dh_checks
    #
    # @ref lodel2_dh_datas_construction "Data construction section"
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname : the field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    #
    # @warning DO NOT REIMPLEMENT THIS METHOD IN A CUSTOM DATAHANDLER (see
    #             @ref _construct_data() and @ref lodel2_dh_check_impl )
    # @warning the data argument looks like a dict but is not a dict
    #             see @ref base_classes.DatasConstructor "DatasConstructor" and
    # @todo A implémenter
    def check_data_consistency(self, emcomponent, fname, datas):
        return self._check_data_consistency(emcomponent, fname, datas)


    ##
    # @brief Designed to be reimplemented by child classes
    #
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname : the field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    #
    # @see check_data_consistency() lodel2_dh_check_impl
    def _check_data_consistency(self, emcomponent, fname, datas):
        return True


    ##
    # @brief Makes consistency after a query
    #
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname : the field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    #
    # @todo To be implemented
    # @remarks It not clear what is the intent of this method... 
    def make_consistency(self, emcomponent, fname, datas):
        pass


    ##
    # @brief Registers a new data handlers
    #
    # @note Used by plugins.
    # @remarks This method is actually never used anywhere. May consider removing it.
    @classmethod
    def register_new_handler(cls, name, data_handler):
        if not inspect.isclass(data_handler):
            raise ValueError("A class was expected but %s given" % type(data_handler))
        if not issubclass(data_handler, DataHandler):
            raise ValueError("A data handler HAS TO be a child class of DataHandler")
        cls.__custom_handlers[name] = data_handler


    ##
    # @brief Loads all DataHandlers
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


    ##
    # @brief given a field type name, returns the associated python class
    #
    # @param name str : A field type name (not case sensitive)
    # @return DataField child class
    # @throw NameError
    #
    # @note Would not it be better to prefix the DataHandler name with the
    #        plugin's one so that it is ensured names are unique? 
    # @remarks "do/get what from name?" Consider renaming this method (e.g. 
    #            'get_datafield_from_name')
    @classmethod
    def from_name(cls, name):
        cls.load_base_handlers()
        all_handlers = dict(cls._base_handlers, **cls.__custom_handlers)
        name = name.lower()
        
        if name not in all_handlers:
            raise NameError("No data handlers named '%s'" % (name,))
        return all_handlers[name]


    ##
    # @brief List all DataHandlers
    # @return a dict with, display_name for keys, and a dict for value
    # @remarks ATM, solely used by the EditorialModel.
    # @remarks EditorialModel own class does nothing but calls this class.
    #            Moreover, nothing calls it anyway.
    # @remarks It also seems like it is an EM related concern, and has
    #            nothing to do with this class. That list appears to be doing
    #            a purely presentational job. Isn't that a serialization instead?
    @classmethod
    def list_data_handlers(cls):
        cls.load_base_handlers()
        all_handlers = dict(cls._base_handlers, **cls.__custom_handlers)
        list_dh = dict()
        for hdl in all_handlers:
            options = dict({'nullable': hdl.nullable,
                            'internal': hdl.internal,
                            'immutable': hdl.immutable,
                            'primary_key': hdl.primary_key}, hdl.options_spec)
            list_dh[hdl.display_name] = {'help_text': hdl.help_text, 'options': options}

        return list_dh


    ##
    # @brief Return the module name to import in order to use the DataHandler
    # @param datahandler_name str : Data handler name
    # @return str
    # @remarks consider renaming this (e.g. "datahandler_module_name")
    @classmethod
    def module_name(cls, datahandler_name):
        datahandler_name = datahandler_name.lower()
        handler_class = cls.from_name(datahandler_name)
        return '{module_name}.{class_name}'.format(
            module_name=handler_class.__module__,
            class_name=handler_class.__name__
        )


    ##
    # @brief __hash__ implementation for field types
    def __hash__(self):
        hash_dats = [self.__class__.__module__]
        for kdic in sorted([k for k in self.__dict__.keys() if not k.startswith('_')]):
            hash_dats.append((kdic, getattr(self, kdic)))
        return hash(tuple(hash_dats))


##
# @brief Base class for data data handler (by opposition with references)
# @ingroup lodel2_datahandlers
class DataField(DataHandler):
    pass


##
# @brief Abstract class for all references
# @ingroup lodel2_datahandlers
#
# References are fields that stores a reference to another
# editorial object
# @todo Construct data implementation : transform the data into a LeObject instance
class Reference(DataHandler):
    
    base_type = "ref"
    
    ##
    # @brief Instantiation
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param back_reference tuple | None : tuple containing (LeObject child class, field name)
    # @param internal bool | string: if False, the field is not internal
    # @param **kwargs : other arguments
    # @throw ValueError
    # @remarks internal may hold the string value 'automatic'. So far, nothing
    #                mentions what that means, and nothing seems to be aware
    #                of an 'automatic' value (at least not in leapi package)
    def __init__(self, allowed_classes=None, back_reference=None, internal=False, **kwargs):
        self.__allowed_classes = set() if allowed_classes is None else set(allowed_classes)
        ##
        # @note what is "useful to Jinja 2"?
        # For now useful to jinja 2
        self.allowed_classes = list() if allowed_classes is None else allowed_classes
        if back_reference is not None:
            if len(back_reference) != 2:
                raise ValueError(
                    "A tuple (classname, fieldname) expected but got '%s'" % back_reference)
            ##
            # @note Why is there commented out code? Should it be deleted? Ractivated?
            # if not issubclass(lodel.leapi.leobject.LeObject, back_reference[0])
            # or not isinstance(back_reference[1], str):
            # raise TypeError("Back reference was expected to be a tuple(<class LeObject>, str)
            # but got : (%s, %s)" % (back_reference[0], back_reference[1]))
        self.__back_reference = back_reference
        super().__init__(internal=internal, **kwargs)


    ##
    # @brief Method designed to return an empty value for this kind of
    # multipleref
    # @remarks purpose!?
    @classmethod
    def empty(cls):
        return None


    ##
    # @brief Property that takes value of a copy of the back_reference tuple
    @property
    def back_reference(self):
        return copy.copy(self.__back_reference)


    ##
    # @brief Property that takes value of datahandler of the backreference or
    # None
    @property
    def back_ref_datahandler(self):
        if self.__back_reference is None:
            return None
        return self.__back_reference[0].data_handler(self.__back_reference[1])

    @property
    def linked_classes(self):
        return copy.copy(self.__allowed_classes)


    ##
    # @brief Sets a back reference.
    def _set_back_reference(self, back_reference):
        self.__back_reference = back_reference


    ##
    # @brief Check and cast value in the appropriate type
    #
    # @param value 
    # @throw FieldValidationError if value is an appropriate type
    # @return value
    # @todo implement the check when we have LeObject uid check value
    def _check_data_value(self, value):
        from lodel.leapi.leobject import LeObject
        value = super()._check_data_value(value)
        if not (hasattr(value, '__class__') and
                issubclass(value.__class__, LeObject)):
            if self.__allowed_classes:
                rcls = list(self.__allowed_classes)[0]
                uidname = rcls.uid_fieldname()[0]  # TODO multiple uid is broken
                uiddh = rcls.data_handler(uidname)
                value = uiddh._check_data_value(value)
            else:
                raise FieldValidationError(
                    "Reference datahandler can not check this value %s if any allowed_class is allowed. " % value)
        return value


    ##
    # @brief Check data consistency
    #
    # @param emcomponent EmComponent :
    # @param fname string : the field name
    # @param datas dict : dict storing fields values
    # @return bool | Exception :
    #
    # @todo check for performance issues and checks logic
    # @warning composed uid capabilities are broken
    # @remarks Is that really a legitimate case of retuning an Exception object? 
    def check_data_consistency(self, emcomponent, fname, datas):
        rep = super().check_data_consistency(emcomponent, fname, datas)
        if isinstance(rep, Exception):
            return rep
        if self.back_reference is None:
            return True
        ##
        # @todo Reimplement instance fetching in construct data
        # @remarks Set the previous todo as one, looked like it was intended to be.
        target_class = self.back_reference[0]
        if target_class not in self.__allowed_classes:
            logger.warning('Class of the back_reference given is not an allowed class')
            return False
        value = datas[fname]
        ##
        # @warning multi uid broken here
        # @remarks Why is that broken? Any clue? Set as a warning.
        target_uidfield = target_class.uid_fieldname()[0]  
        obj = target_class.get([(target_uidfield, '=', value)])
        if len(obj) == 0:
            logger.warning('Object referenced does not exist')
            return False
        return True


    ##
    # @brief Utility method designed to fetch referenced objects
    #
    # @param value mixed : the field value
    # @throw NotImplementedError
    # @remarks Not implemented? Consider renaming?
    def get_referenced(self, value):
        raise NotImplementedError


##
# @brief DataHandler for single reference to another object
#
# An instance of this class acts like a "foreign key" to another object
class SingleRef(Reference):


    def __init__(self, allowed_classes=None, **kwargs):
        super().__init__(allowed_classes=allowed_classes, **kwargs)


    ##
    # @brief Checks and casts value to the appropriate type
    #
    # @param value: mixed
    # @throw FieldValidationError if value is inappropriate or can not be cast
    # @return mixed
    def _check_data_value(self, value):
        value = super()._check_data_value(value)
        return value


    ##
    # @brief Utility method to fetch referenced objects
    #
    # @param value mixed : the field value
    # @return A LeObject child class instance
    # @throw LodelDataHandlerConsistencyException if no referenced object found
    # @remarks Consider renaming (e.g. get_referenced_object)?
    def get_referenced(self, value):
        for leo_cls in self.linked_classes:
            res = leo_cls.get_from_uid(value)
            if res is not None:
                return res
        raise LodelDataHandlerConsistencyException("Unable to find \
referenced object with uid %s" % value)


##
# @brief DataHandler for multiple references to another object
# @ingroup lodel2_datahandlers
#
# The fields using this data handlers are like SingleRef but can store multiple
# references in one field.
# @note for the moment split on ',' chars
class MultipleRef(Reference):

    ##
    # @brief Constructor
    #
    # @param max_item int | None : indicate the maximum number of item referenced
    #         by this field, None mean no limit
    def __init__(self, max_item=None, **kwargs):
        self.max_item = max_item
        super().__init__(**kwargs)

    ##
    # @brief Method designed to return an empty value for this kind of
    #         multipleref
    # @remarks Purpose!?
    @classmethod
    def empty(cls):
        return []


    ##
    # @brief Check and cast value in appropriate type
    # @param value mixed
    # @throw FieldValidationError if value is unappropriate or can not be cast
    # @return value
    # @todo  Writing test error for errors when stored multiple references in one field
    def _check_data_value(self, value):
        value = DataHandler._check_data_value(self, value)
        if not hasattr(value, '__iter__'):
            raise FieldValidationError(
                "MultipleRef has to be an iterable or a string, '%s' found" % value)
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
            raise FieldValidationError(
                "MultipleRef have for invalid values [%s]  :" % (",".join(error_list)))
        return new_val

    ##
    # @brief Utility method designed to fetch referenced objects
    #
    # @param values mixed : the field values
    # @return A list of LeObject child class instance
    # @throw LodelDataHandlerConsistencyException if some referenced objects
    # were not found
    def get_referenced(self, values):
        if values is None or len(values) == 0:
            return list()
        left = set(values)
        values = set(values)
        res = list()
        for leo_cls in self.linked_classes:
            uidname = leo_cls.uid_fieldname()[0]  # MULTIPLE UID BROKEN HERE
            tmp_res = leo_cls.get(('%s in (%s)' % (uidname, ','.join(
                [str(l) for l in left]))))
            left ^= set((leo.uid() for leo in tmp_res))
            res += tmp_res
            if len(left) == 0:
                return res
        raise LodelDataHandlerConsistencyException("Unable to find \
some referenced objects. Following uids were not found : %s" % ','.join(left))


##
# @brief Class designed to handle data access while field types are constructing data
# @ingroup lodel2_datahandlers
#
# This class is designed to allow automatic scheduling of construct_data calls.
#
# In theory it has the ability to detect circular dependencies
# @todo test circular deps detection
# @todo test circular deps false positive
# @remarks Would not it be better to make sure what the code actually is doing? 
class DatasConstructor(object):

    ##
    # @brief Init a DatasConstructor
    #
    # @param leobject LeObject
    # @param datas dict : dict with field name as key and field values as value
    # @param fields_handler dict : dict with field name as key and data handler instance as value
    def __init__(self, leobject, datas, fields_handler):
        self._leobject = leobject
        self._datas = copy.copy(datas)
        # Stores fieldtypes
        self._fields_handler = fields_handler
        # Stores list of fieldname for constructed 
        self._constructed = []
        # Stores construct calls list
        self._construct_calls = []


    ##
    # @brief Implements the dict.keys() method on instance
    #
    # @return list
    def keys(self):
        return self._datas.keys()


    ##
    # @brief Allows to access the instance like a dict
    #
    # @param fname string: The field name
    # @return field values
    # @throw RuntimeError
    #
    # @note Determine return type 
    def __getitem__(self, fname):
        if fname not in self._constructed:
            if fname in self._construct_calls:
                raise RuntimeError('Probably circular dependencies in fieldtypes')
            cur_value = self._datas[fname] if fname in self._datas else None
            self._datas[fname] = self._fields_handler[fname].construct_data(
                self._leobject, fname, self, cur_value)
            self._constructed.append(fname)
        return self._datas[fname]


    ##
    # @brief Allows to set instance values like a dict
    #
    # @warning Should not append in theory
    #
    # @remarks Why is a warning issued any time we call this method?  
    def __setitem__(self, fname, value):
        self._datas[fname] = value
        warnings.warn("Setting value of an DatasConstructor instance")


##
# @brief Class designed to handle a DataHandler option
class DatahandlerOption(MlNamedObject):


    ##
    # @brief instantiates a new DataHandlerOption object
    #
    # @param id str
    # @param display_name MlString
    # @param help_text MlString
    # @param validator function
    def __init__(self, id, display_name, help_text, validator):
        self.__id = id
        self.__validator = validator
        super().__init__(display_name, help_text)

    ##
    # @brief Accessor to the id property.
    @property
    def id(self):
        return self.__id

    ##
    # @brief checks a value corresponding to this option is valid
    #
    # @param value mixed
    # @return cast value
    # @throw ValueError
    def check_value(self, value):
        try:
            return self.__validator(value)
        except ValidationError:
            raise ValueError()
