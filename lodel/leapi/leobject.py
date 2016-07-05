#-*- coding: utf-8 -*-

import importlib
import warnings
import copy

from lodel.plugin import Plugin
from lodel import logger
from lodel.settings import Settings
from lodel.settings.utils import SettingsError
from .query import LeInsertQuery, LeUpdateQuery, LeDeleteQuery, LeGetQuery
from .exceptions import *
from lodel.plugin.hooks import LodelHook
from lodel.leapi.datahandlers.base_classes import DatasConstructor

##@brief Stores the name of the field present in each LeObject that indicates
#the name of LeObject subclass represented by this object
CLASS_ID_FIELDNAME = "classname"

##@brief Wrapper class for LeObject getter & setter
#
# This class intend to provide easy & friendly access to LeObject fields values 
# without name collision problems
# @note Wrapped methods are : LeObject.data() & LeObject.set_data()
class LeObjectValues(object):
    
    ##@brief Construct a new LeObjectValues
    # @param set_callback method : The LeObject.set_datas() method of corresponding LeObject class
    # @param get_callback method : The LeObject.get_datas() method of corresponding LeObject class
    def __init__(self, fieldnames_callback, set_callback, get_callback):
        self._setter = set_callback
        self._getter = get_callback
    
    ##@brief Provide read access to datas values
    # @note Read access should be provided for all fields
    # @param fname str : Field name
    def __getattribute__(self, fname):
        getter = super().__getattribute__('_getter')
        return getter(fname)
    
    ##@brief Provide write access to datas values
    # @note Write acces shouldn't be provided for internal or immutable fields
    # @param fname str : Field name
    # @param fval * : the field value
    def __setattribute__(self, fname, fval):
        setter = super().__getattribute__('_setter')
        return setter(fname, fval)
        

class LeObject(object):
 
    ##@brief boolean that tells if an object is abtract or not
    _abstract = None
    ##@brief A dict that stores DataHandler instances indexed by field name
    _fields = None
    ##@brief A tuple of fieldname (or a uniq fieldname) representing uid
    _uid = None 
    ##@brief Read only datasource ( see @ref lodel2_datasources )
    _ro_datasource = None
    ##@brief Read & write datasource ( see @ref lodel2_datasources )
    _rw_datasource = None
    ##@brief Store the list of child classes
    _child_classes = None

    def __new__(cls, **kwargs):
        
        self = object.__new__(cls)
        ##@brief A dict that stores fieldvalues indexed by fieldname
        self.__datas = { fname:None for fname in self._fields }
        ##@brief Store a list of initianilized fields when instanciation not complete else store True
        self.__initialized = list()
        ##@brief Datas accessor. Instance of @ref LeObjectValues
        self.d = LeObjectValues(self.fieldnames, self.set_data, self.data)
        for fieldname, fieldval in kwargs.items():
            self.__datas[fieldname] = fieldval
            self.__initialized.append(fieldname)
        self.__is_initialized = False
        self.__set_initialized()
        return self

    ##@brief Construct an object representing an Editorial component
    # @note Can be considered as EmClass instance
    def __init__(self, **kwargs):
        if self._abstract:
            raise NotImplementedError("%s is abstract, you cannot instanciate it." % self.__class__.__name__ )

        # Checks that uid is given
        for uid_name in self._uid:
            if uid_name not in kwargs:
                raise LeApiError("Cannot instanciate a LeObject without it's identifier")
            self.__datas[uid_name] = kwargs[uid_name]
            del(kwargs[uid_name])
            self.__initialized.append(uid_name)

        # Processing given fields
        allowed_fieldnames = self.fieldnames(include_ro = False)
        err_list = dict()
        for fieldname, fieldval in kwargs.items():
            if fieldname not in allowed_fieldnames:
                if fieldname in self._fields:
                    err_list[fieldname] = LeApiError(
                        "Value given but the field is internal")
                else:
                    err_list[fieldname] = LeApiError(
                        "Unknown fieldname : '%s'" % fieldname)
            else:
                self.__datas[fieldname] = fieldval
                self.__initialized.append(fieldname)
        if len(err_list) > 0:
            raise LeApiErrors(msg = "Unable to __init__ %s" % self.__class__,
                exceptions = err_list)
        self.__set_initialized()
    
    #-----------------------------------#
    #   Fields datas handling methods   #
    #-----------------------------------#

    ##@brief @property True if LeObject is initialized else False
    @property
    def initialized(self):
        return self.__is_initialized
    
    ##@return The uid field name
    @classmethod
    def uid_fieldname(cls):
        return cls._uid

    ##@brief Return a list of fieldnames
    # @param include_ro bool : if True include read only field names
    # @return a list of str
    @classmethod
    def fieldnames(cls, include_ro = False):
        if not include_ro:
            return [ fname for fname in cls._fields if not cls._fields[fname].is_internal() ]
        else:
            return list(cls._fields.keys())
 
    @classmethod
    def name2objname(cls, name):
        return name.title()
    
    ##@brief Return the datahandler asssociated with a LeObject field
    # @param fieldname str : The fieldname
    # @return A data handler instance
    @classmethod
    def data_handler(cls, fieldname):
        if not fieldname in cls._fields:
            raise NameError("No field named '%s' in %s" % (fieldname, cls.__name__))
        return cls._fields[fieldname]
    
    ##@brief Return a LeObject child class from a name
    # @warning This method has to be called from dynamically generated LeObjects
    # @param leobject_name str : LeObject name
    # @return A LeObject child class
    # @throw NameError if invalid name given
    @classmethod
    def name2class(cls, leobject_name):
        if cls.__module__ == 'lodel.leapi.leobject':
            raise NotImplementedError("Abstract method")
        mod = importlib.import_module(cls.__module__)
        try:
            return getattr(mod, leobject_name)
        except (AttributeError, TypeError) :
            raise LeApiError("No LeObject named '%s'" % leobject_name)
    
    @classmethod
    def is_abstract(cls):
        return cls._abstract
    
    ##@brief Field data handler getter
    #@param fieldname str : The field name
    #@return A datahandler instance
    #@throw NameError if the field doesn't exist
    @classmethod
    def field(cls, fieldname):
        try:
            return cls._fields[fieldname]
        except KeyError:
            raise NameError("No field named '%s' in %s" % ( fieldname,
                                                            cls.__name__))
    ##@return A dict with fieldname as key and datahandler as instance
    @classmethod
    def fields(cls, include_ro = False):
        if include_ro:
            return copy.copy(cls._fields)
        else:
            return {fname:cls._fields[fname] for fname in cls._fields if not cls._fields[fname].is_internal()}
    
    ##@brief Return the list of parents classes
    #
    #@note the first item of the list is the current class, the second is it's
    #parent etc...
    #@param cls
    #@warning multiple inheritance broken by this method
    #@return a list of LeObject child classes
    #@todo multiple parent capabilities implementation
    @classmethod
    def hierarch(cls):
        res = [cls]
        cur = cls
        while True:
            cur = cur.__bases__[0] # Multiple inheritance broken HERE
            if cur in (LeObject, object):
                break
            else:
                res.append(cur)
        return res
    
    ##@brief Return a tuple a child classes
    #@return a tuple of child classes
    @classmethod
    def child_classes(cls):
        return copy.copy(cls._child_classes)
        

    ##@brief Return the parent class that is the "source" of uid
    #
    #The method goal is to return the parent class that defines UID.
    #@return a LeObject child class or false if no UID defined
    @classmethod
    def uid_source(cls):
        if cls._uid is None or len(cls._uid) == 0:
            return False
        hierarch = cls.hierarch()
        prev = hierarch[0]
        uid_handlers = set( cls._fields[name] for name in cls._uid )
        for pcls in cls.hierarch()[1:]:
            puid_handlers = set(cls._fields[name] for name in pcls._uid)
            if set(pcls._uid) != set(prev._uid) \
                or puid_handlers != uid_handlers:
                break
            prev = pcls
        return prev
    
    ##@brief Initialise both datasources (ro and rw)
    #
    #This method is used once at dyncode load to replace the datasource string
    #by a datasource instance to avoid doing this operation for each query
    #@see LeObject::_init_datasource()
    @classmethod
    def _init_datasources(cls):
        if isinstance(cls._datasource_name, str):
            rw_ds = ro_ds = cls._datasource_name
        else:
            ro_ds, rw_ds = cls._datasource_name
        #Read only datasource initialisation
        cls._ro_datasource = cls._init_datasource(ro_ds, True)
        if cls._ro_datasource is None:
            log_msg = "No read only datasource set for LeObject %s"
            log_msg %= cls.__name__
            logger.debug(log_msg)
        else:
            log_msg = "Read only datasource '%s' initialized for LeObject %s"
            log_msg %= (ro_ds, cls.__name__)
            logger.debug(log_msg)
        #Read write datasource initialisation
        cls._rw_datasource = cls._init_datasource(rw_ds, False)
        if cls._ro_datasource is None:
            log_msg = "No read/write datasource set for LeObject %s"
            log_msg %= cls.__name__
            logger.debug(log_msg)
        else:
            log_msg = "Read/write datasource '%s' initialized for LeObject %s"
            log_msg %= (ro_ds, cls.__name__)
            logger.debug(log_msg)
        

    ##@brief Replace the _datasource attribute value by a datasource instance
    #
    #This method is used once at dyncode load to replace the datasource string
    #by a datasource instance to avoid doing this operation for each query
    #@param ds_name str : The name of the datasource to instanciate
    #@param ro bool : if true initialise the _ro_datasource attribute else
    #initialise _rw_datasource attribute
    #@throw SettingsError if an error occurs
    @classmethod
    def _init_datasource(cls, ds_name, ro):
        expt_msg = "In LeAPI class '%s' " % cls.__name__
        if ds_name not in Settings.datasources._fields:
            #Checking that datasource exists
            expt_msg += "Unknown or unconfigured datasource %s for class %s"
            expt_msg %= (ds_name, cls.__name__)
            raise SettingsError(expt_msg)
        try:
            #fetching plugin name
            ds_plugin_name, ds_identifier = cls._get_ds_plugin_name(ds_name, ro)
        except NameError:
            expt_msg += "Datasource %s is missconfigured, missing identifier."
            expt_msg %= ds_name
            raise SettingsError(expt_msg)
        except RuntimeError:
            expt_msg += "Error in datasource %s configuration. Trying to use \
a read only as a read&write datasource"
            expt_msg %= ds_name
            raise SettingsError(expt_msg)
        except ValueError as e:
            expt_msg += str(e)
            raise SettingsError(expt_msg)
        
        try:
            ds_conf = cls._get_ds_connection_conf(ds_identifier, ds_plugin_name)
        except NameError as e:
            expt_msg += str(e)
            raise SettingsError(expt_msg)
        #Checks that the datasource plugin exists
        ds_plugin_module = Plugin.get(ds_plugin_name).loader_module()
        try:
            datasource_class = getattr(ds_plugin_module, "Datasource")
        except AttributeError as e:
            expt_msg += "The datasource plugin %s seems to be invalid. Error \
raised when trying to import Datasource"
            expt_msg %= ds_identifier
            raise SettingsError(expt_msg)

        return datasource_class(**ds_conf)

    ##@brief Try to fetch a datasource configuration
    #@param ds_identifier str : datasource name
    #@param ds_plugin_name : datasource plugin name
    #@return a dict containing datasource initialisation options
    #@throw NameError if a datasource plugin or instance cannot be found
    @staticmethod
    def _get_ds_connection_conf(ds_identifier,ds_plugin_name):
        if ds_plugin_name not in Settings.datasource._fields:
            msg = "Unknown or unconfigured datasource plugin %s"
            msg %= ds_plugin
            raise NameError(msg)
        ds_conf = getattr(Settings.datasource, ds_plugin_name)
        if ds_identifier not in ds_conf._fields:
            msg = "Unknown or unconfigured datasource instance %s"
            msg %= ds_identifier
            raise NameError(msg)
        ds_conf = getattr(ds_conf, ds_identifier)
        return {k: getattr(ds_conf,k) for k in ds_conf._fields }

    ##@brief fetch datasource plugin name
    #@param ds_name str : datasource name
    #@param ro bool : if true consider the datasource as read only
    #@return a tuple(DATASOURCE_PLUGIN_NAME, DATASOURCE_CONNECTION_NAME)
    #@throw NameError if datasource identifier not found
    #@throw RuntimeError if datasource is read_only but ro flag was false
    @staticmethod
    def _get_ds_plugin_name(ds_name, ro):
        datasource_orig_name = ds_name
        # fetching connection identifier given datasource name
        ds_identifier = getattr(Settings.datasources, ds_name)
        read_only = getattr(ds_identifier, 'read_only')
        try:
            ds_identifier = getattr(ds_identifier, 'identifier')
        except NameError as e:
            raise e
        if read_only and not ro:
            raise RuntimeError()
        res = ds_identifier.split('.')
        if len(res) != 2:
            raise ValueError("expected value for identifier is like \
DS_PLUGIN_NAME.DS_INSTANCE_NAME. But got %s" % ds_identifier)
        return res
    
    ##@brief Return the uid of the current LeObject instance
    #@return the uid value
    #@warning Broke multiple uid capabilities
    def uid(self):
        return self.data(self._uid[0])

    ##@brief Read only access to all datas
    # @note for fancy data accessor use @ref LeObject.g attribute @ref LeObjectValues instance
    # @param name str : field name
    # @return the Value
    # @throw RuntimeError if the field is not initialized yet
    # @throw NameError if name is not an existing field name
    def data(self, field_name):
        if field_name not in self._fields.keys():
            raise NameError("No such field in %s : %s" % (self.__class__.__name__, field_name))
        if not self.initialized and field_name not in self.__initialized:
            raise RuntimeError("The field %s is not initialized yet (and have no value)" % field_name)
        return self.__datas[field_name]
    
    ##@brief Read only access to all datas
    #@return a dict representing datas of current instance
    def datas(self, internal = False):
        return {fname:self.data(fname) for fname in self.fieldnames(internal)}
        
    
    ##@brief Datas setter
    # @note for fancy data accessor use @ref LeObject.g attribute @ref LeObjectValues instance
    # @param fname str : field name
    # @param fval * : field value
    # @return the value that is really set
    # @throw NameError if fname is not valid
    # @throw AttributeError if the field is not writtable
    def set_data(self, fname, fval):
        if fname not in self.fieldnames(include_ro = False):
            if fname not in self._fields.keys():
                raise NameError("No such field in %s : %s" % (self.__class__.__name__, fname))
            else:
                raise AttributeError("The field %s is read only" % fname)
        self.__datas[fname] = fval
        if not self.initialized and fname not in self.__initialized:
            # Add field to initialized fields list
            self.__initialized.append(fname)
            self.__set_initialized()
        if self.initialized:
            # Running full value check
            ret = self.__check_modified_values()
            if ret is None:
                return self.__datas[fname]
            else:
                raise LeApiErrors("Data check error", ret)
        else:
            # Doing value check on modified field
            # We skip full validation here because the LeObject is not fully initialized yet
            val, err = self._fields[fname].check_data_value(fval)
            if isinstance(err, Exception):
                #Revert change to be in valid state
                del(self.__datas[fname])
                del(self.__initialized[-1])
                raise LeApiErrors("Data check error", {fname:err})
            else:
                self.__datas[fname] = val
    
    ##@brief Update the __initialized attribute according to LeObject internal state
    #
    # Check the list of initialized fields and set __initialized to True if all fields initialized
    def __set_initialized(self):
        if isinstance(self.__initialized, list):
            expected_fields = self.fieldnames(include_ro = False) + self._uid
            if set(expected_fields) == set(self.__initialized):
                self.__is_initialized = True

    ##@brief Designed to be called when datas are modified
    #
    # Make different checks on the LeObject given it's state (fully initialized or not)
    # @return None if checks succeded else return an exception list
    def __check_modified_values(self):
        err_list = dict()
        if self.__initialized is True:
            # Data value check
            for fname in self.fieldnames(include_ro = False):
                val, err = self._fields[fname].check_data_value(self.__datas[fname])
                if err is not None:
                    err_list[fname] = err
                else:
                    self.__datas[fname] = val
            # Data construction
            if len(err_list) == 0:
                for fname in self.fieldnames(include_ro = True):
                    try:
                        field = self._fields[fname]
                        self.__datas[fname] = fields.construct_data(    self,
                                                                        fname,
                                                                        self.__datas,
                                                                        self.__datas[fname]
                        )
                    except Exception as e:
                        err_list[fname] = e
            # Datas consistency check
            if len(err_list) == 0:
                for fname in self.fieldnames(include_ro = True):
                    field = self._fields[fname]
                    ret = field.check_data_consistency(self, fname, self.__datas)
                    if isinstance(ret, Exception):
                        err_list[fname] = ret
        else:
            # Data value check for initialized datas
            for fname in self.__initialized:
                val, err = self._fields[fname].check_data_value(self.__datas[fname])
                if err is not None:
                    err_list[fname] = err
                else:
                    self.__datas[fname] = val
        return err_list if len(err_list) > 0 else None

    #--------------------#
    #   Other methods    #
    #--------------------#
    
    ##@brief Temporary method to set private fields attribute at dynamic code generation
    #
    # This method is used in the generated dynamic code to set the _fields attribute
    # at the end of the dyncode parse
    # @warning This method is deleted once the dynamic code loaded
    # @param field_list list : list of EmField instance
    # @param cls
    @classmethod
    def _set__fields(cls, field_list):
        cls._fields = field_list
        
    ## @brief Check that datas are valid for this type
    # @param datas dict : key == field name value are field values
    # @param complete bool : if True expect that datas provide values for all non internal fields
    # @param allow_internal bool : if True don't raise an error if a field is internal
    # @param cls
    # @return Checked datas
    # @throw LeApiDataCheckError if errors reported during check
    @classmethod
    def check_datas_value(cls, datas, complete = False, allow_internal = True):
        err_l = dict() #Error storing
        correct = set() #valid fields name
        mandatory = set() #mandatory fields name
        for fname, datahandler in cls._fields.items():
            if allow_internal or not datahandler.is_internal():
                correct.add(fname)
                if complete and not hasattr(datahandler, 'default'):
                    mandatory.add(fname)
        provided = set(datas.keys())
        # searching for unknow fields
        for u_f in provided - correct:
            #Here we can check if the field is invalid or rejected because
            # it is internel
            err_l[u_f] = AttributeError("Unknown or unauthorized field '%s'" % u_f)
        # searching for missing mandatory fieldsa
        for missing in mandatory - provided:
            err_l[missing] = AttributeError("The data for field '%s' is missing" % missing)
        #Checks datas
        checked_datas = dict()
        for name, value in [ (name, value) for name, value in datas.items() if name in correct ]:
            dh = cls._fields[name]
            res = dh.check_data_value(value)
            checked_datas[name], err = res
            if err:
                err_l[name] = err

        if len(err_l) > 0:
            raise LeApiDataCheckErrors("Error while checking datas", err_l)
        return checked_datas

    ##@brief Check and prepare datas
    # 
    # @warning when complete = False we are not able to make construct_datas() and _check_data_consistency()
    # 
    # @param datas dict : {fieldname : fieldvalue, ...}
    # @param complete bool : If True you MUST give all the datas
    # @param allow_internal : Wether or not interal fields are expected in datas
    # @param cls
    # @return Datas ready for use
    # @todo: complete is very unsafe, find a way to get rid of it
    @classmethod
    def prepare_datas(cls, datas, complete=False, allow_internal=True):
        if not complete:
            warnings.warn("\nActual implementation can make broken datas \
construction and consitency when datas are not complete\n")
        ret_datas = cls.check_datas_value(datas, complete, allow_internal)
        if isinstance(ret_datas, Exception):
            raise ret_datas

        if complete:
            ret_datas = cls._construct_datas(ret_datas)
            cls._check_datas_consistency(ret_datas)
        return ret_datas

    ## @brief Construct datas values
    #
    # @param cls
    # @param datas dict : Datas that have been returned by LeCrud.check_datas_value() methods
    # @return A new dict of datas
    # @todo IMPLEMENTATION
    @classmethod
    def _construct_datas(cls, datas):
        constructor = DatasConstructor(cls, datas, cls._fields)
        ret = {
                fname:constructor[fname]
                for fname, ftype in cls._fields.items()
                if not ftype.is_internal() or ftype.internal != 'autosql'
        }
        return ret

    ## @brief Check datas consistency
    # 
    # @warning assert that datas is complete
    # @param cls
    # @param datas dict : Datas that have been returned by LeCrud._construct_datas() method
    # @throw LeApiDataCheckError if fails
    @classmethod
    def _check_datas_consistency(cls, datas):
        err_l = []
        err_l = dict()
        for fname, dh in cls._fields.items():
            ret = dh.check_data_consistency(cls, fname, datas)
            if isinstance(ret, Exception):
                err_l[fname] = ret

        if len(err_l) > 0:
            raise LeApiDataCheckError("Datas consistency checks fails", err_l)
    
    ## @brief Add a new instance of LeObject
    # @return a new uid en case of success, False otherwise
    @classmethod
    def insert(cls, datas):
        query = LeInsertQuery(cls)
        return query.execute(datas)

    ## @brief Update an instance of LeObject
    #
    #@param datas : list of new datas 
    def update(self, datas = None):
        datas = self.datas(internal=False) if datas is None else datas
        uids = self._uid
        query_filter = list()
        for uid in uids:
            query_filter.append((uid, '=', self.data(uid)))
        try:
            query = LeUpdateQuery(self.__class__, query_filter)
        except Exception as err:
            raise err
            
        try:
            result = query.execute(datas)
        except Exception as err:
            raise err

        return result
    
    ## @brief Delete an instance of LeObject
    #
    #@return 1 if the objet has been deleted
    def delete(self):
        uids = self._uid
        query_filter = list()
        for uid in uids:
            query_filter.append((uid, '=', self.data(uid)))

        query = LeDeleteQuery(self.__class__, query_filter)

        result = query.execute()

        return result
    
    ## @brief Delete instances of LeObject
    #@param uids a list: lists of (fieldname, fieldvalue), with fieldname in cls._uids
    #@returns the 
    @classmethod
    def delete_bundle(cls, query_filters):
        deleted = 0
        try:
            query = LeDeleteQuery(cls, query_filters)
        except Exception as err:
            raise err
                
        try:
            result = query.execute()
        except Exception as err:
            raise err
        if not result is None:
            deleted += result
        return deleted
            
    ## @brief Get instances of LeObject
    #
    #@param target_class LeObject : class of object the query is about
    
    #@param query_filters dict : (filters, relational filters), with filters is a list of tuples : (FIELD, OPERATOR, VALUE) )
    #@param field_list list|None : list of string representing fields see 
    #@ref leobject_filters
    #@param order list : A list of field names or tuple (FIELDNAME,[ASC | DESC])
    #@param group list : A list of field names or tuple (FIELDNAME,[ASC | DESC])
    #@param limit int : The maximum number of returned results
    #@param offset int : offset
    #@param Inst
    #@return a list of items (lists of (fieldname, fieldvalue))
    @classmethod
    def get(cls, query_filters, field_list=None, order=None, group=None, limit=None, offset=0):
        if field_list is not None:
            for uid in [ uidname
                for uidname in cls.uid_fieldname()
                if uidname not in field_list ]:
                field_list.append(uid)
            if CLASS_ID_FIELDNAME not in field_list:
                field_list.append(CLASS_ID_FIELDNAME)
        try:
            query = LeGetQuery(
                cls, query_filters = query_filters, field_list = field_list,
                order = order, group = group, limit = limit, offset = offset)
        except ValueError as err:
            raise err
            
        try:
            result = query.execute()
        except Exception as err:
            raise err
        
        objects = list()
        for res in result:
            res_cls = cls.name2class(res[CLASS_ID_FIELDNAME])
            inst = res_cls.__new__(res_cls,**res)
            objects.append(inst)
        
        return objects
    


        
        

