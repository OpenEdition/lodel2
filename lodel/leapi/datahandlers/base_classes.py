# -*- coding: utf-8 -*-

## @package lodel.leapi.datahandlers.base_classes Define all base/abstract class for data handlers
#
# Contains custom exceptions too

import copy
import importlib
import inspect
import warnings

from lodel import logger


class FieldValidationError(Exception):
    pass

##@brief Base class for all data handlers
#@ingroup lodel2_datahandlers
class DataHandler(object):
    
    _HANDLERS_MODULES = ('datas_base', 'datas', 'references')
    ##@brief Stores the DataHandler childs classes indexed by name
    _base_handlers = None
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

    def is_primary_key(self):
        return self.primary_key

    ##@brief checks if a fieldtype is internal
    # @return bool
    def is_internal(self):
        return self.internal is not False

    ##@brief calls the data_field defined _check_data_value() method
    #@ingroup lodel2_dh_checks
    #@warning DO NOT REIMPLEMENT THIS METHOD IN A CUSTOM DATAHANDLER (see
    #@ref _construct_data() and @ref lodel2_dh_check_impl )
    #@return tuple (value, error|None)
    def check_data_value(self, value):
        if value is None:
            if not self.nullable:
                return None, TypeError("'None' value but field is not nullable")

            return None, None
        return self._check_data_value(value)
    
    ##@brief Designed to be implemented in child classes
    def _check_data_value(self, value):
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
#@ingroup lodel2_datahandlers
class DataField(DataHandler):
    pass

##@brief Abstract class for all references
#@ingroup lodel2_datahandlers
#
# References are fields that stores a reference to another
# editorial object
#
#
#@todo Check data implementation : check_data = is value an UID or an
#LeObject child instance
#@todo Construct data implementation : transform the data into a LeObject
#instance
#@todo Check data consistency implementation : check that LeObject instance
#is from an allowed class
class Reference(DataHandler):
    base_type="ref"

    ##@brief Instanciation
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param back_reference tuple | None : tuple containing (LeObject child class, fieldname)
    # @param internal bool : if False, the field is not internal
    # @param **kwargs : other arguments
    def __init__(self, allowed_classes = None, back_reference = None, internal=False, **kwargs):
        ##@brief set of allowed LeObject child classes
        self.__allowed_classes = set() if allowed_classes is None else set(allowed_classes)
        ##@brief Stores back references informations
        self.__back_reference = None
        self.__set_back_reference(back_reference)
        super().__init__(internal=internal, **kwargs)
 
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
    def __set_back_reference(self, back_reference):
        if back_reference is None:
            return
        if len(back_reference) != 2:
            raise LodelDataHandlerException("A tuple(LeObjectChild, fieldname) \
expected but got '%s'" % back_reference)
        
        self.__back_reference = back_reference

    ##@brief Check value
    #@param value *
    #@return tuple(value, exception)
    #@todo implement the check when we have LeObject to check value
    def check_data_value(self, value):
        return super().check_data_value(value)



        if isinstance(value, lodel.editorial_model.components.EmClass):
            value = [value]
        for elt in value:
            if not issubclass(elt.__class__, EmClass):
                return None, FieldValidationError("Some elements of this references are not EmClass instances")
            if self.__allowed_classes is not None:
                if not isinstance(elt, self.__allowed_classes):
                    return None, FieldValidationError("Some element of this references are not valids (don't fit with allowed_classes")
        return value

    ##@brief Check datas consistency
    #@param emcomponent EmComponent : An EmComponent child class instance
    #@param fname : the field name
    #@param datas dict : dict storing fields values
    #@return an Exception instance if fails else True
    #@todo check for performance issue and check logics
    #@todo Implements consistency checking on value : Check that the given value
    #points onto an allowed class
    #@warning composed uid capabilities broken here
    def check_data_consistency(self, emcomponent, fname, datas):
        rep = super().check_data_consistency(emcomponent, fname, datas)
        if isinstance(rep, Exception):
            return rep
        if self.back_reference is None:
            return True
        #Checking back reference consistency

        # !! Reimplement instance fetching in construct data !!
        dh = emcomponent.field(fname)
        uid = datas[emcomponent.uid_fieldname()[0]] #multi uid broken here
        target_class = self.back_reference[0]
        target_field = self.back_reference[1]
        target_uidfield = target_class.uid_fieldname()[0] #multi uid broken here
        value = datas[fname]
        
        obj = target_class.get([(target_uidfield , '=', value)])
        
        if len(obj) == 0:
            logger.warning('Object referenced does not exist')
            return False
        
        return True

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
#@ingroup lodel2_datahandlers
#
# The fields using this data handlers are like SingleRef but can store multiple references in one field
# @note for the moment split on ',' chars
class MultipleRef(Reference):
    
    ##
    # @param max_item int | None : indicate the maximum number of item referenced by this field, None mean no limit
    def __init__(self, max_item = None, **kwargs):
        self.max_item = max_item
        super().__init__(**kwargs)

        
    def check_data_value(self, value):
        value, expt = super().check_data_value(value)
        if expt is not None:
            #error in parent
            return value, expt
        elif value is None:
            #none value
            return value, expt

        expt = None
     
        if isinstance(value, str):
            value, expt = super()._check_data_value(value)
        elif not hasattr(value, '__iter__'):
            return None, FieldValidationError("MultipleRef has to be an iterable or a string, '%s' found" % value)
        if self.max_item is not None:
            if self.max_item < len(value):
                return None, FieldValidationError("Too many items")
        return value, expt

    def construct_data(self, emcomponent, fname, datas, cur_value):
        cur_value = super().construct_data(emcomponent, fname, datas, cur_value)
        if cur_value == 'None' or cur_value is None or cur_value == '':
            return None
        emcomponent_fields = emcomponent.fields()
        data_handler = None
        if fname in emcomponent_fields:
            data_handler = emcomponent_fields[fname]
        u_fname = emcomponent.uid_fieldname()
        uidtype = emcomponent.field(u_fname[0]) if isinstance(u_fname, list) else emcomponent.field(u_fname)

        if isinstance(cur_value, str):
            value = cur_value.split(',')
            l_value = [uidtype.cast_type(uid) for uid in value]
        elif isinstance(cur_value, list):
            l_value = list()
            for value in cur_value:
                if isinstance(value,uidtype.cast_type):
                    l_value.append(value)
                else:
                    raise ValueError("The items must be of the same type, string or %s" % (emcomponent.__name__))
        else:
            l_value = None

        if l_value is not None:
            if self.back_reference is not None:
                br_class = self.back_reference[0]
                for br_id in l_value:
                    query_filters = list()
                    query_filters.append((br_class.uid_fieldname()[0], '=', br_id))
                    br_obj = br_class.get(query_filters)
                    if len(br_obj) != 0:
                        br_list = br_obj[0].data(self.back_reference[1])
                        if br_list is None:
                            br_list = list()
                        if br_id not in br_list:
                            br_list.append(br_id)
        return l_value
    
    ## @brief Checks the backreference, updates it if it is not complete
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname : the field name
    # @param datas dict : dict storing fields values
    # @note Not done in case of delete
    def make_consistency(self, emcomponent, fname, datas, type_query):

        dh = emcomponent.field(fname)

        logger.info('Warning : multiple uid capabilities are broken here')
        uid = datas[emcomponent.uid_fieldname()[0]]
        if self.back_reference is not None:
            target_class = self.back_reference[0]
            target_field = self.back_reference[1]
            target_uidfield = target_class.uid_fieldname()[0]
            l_value = datas[fname]

            if l_value is not None:
                for value in l_value:
                    query_filters = list()
                    query_filters.append((target_uidfield , '=', value))
                    obj = target_class.get(query_filters)
                    if len(obj) == 0:
                        logger.warning('Object referenced does not exist')
                        return False
                    l_uids_ref = obj[0].data(target_field)
                    if l_uids_ref is None:
                        l_uids_ref = list()
                    if uid not in l_uids_ref:
                        l_uids_ref.append(uid)
                        obj[0].set_data(target_field, l_uids_ref)
                        obj[0].update()
           
            if type_query == 'update':
                query_filters = list()
                query_filters.append((uid, ' in ', target_field))
                objects = target_class.get(query_filters)
                if l_value is None:
                    l_value = list()
                if len(objects) != len(l_value):
                    for obj in objects:
                        l_uids_ref = obj.data(target_field)
                        if obj.data(target_uidfield) not in l_value:
                            l_uids_ref.remove(uid)
                            obj.set_data(target_field, l_uids_ref)
                            obj.update()

                
## @brief Class designed to handle datas access will fieldtypes are constructing datas
#@ingroup lodel2_datahandlers
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
 
