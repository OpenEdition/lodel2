#-*- coding: utf-8 -*-

import importlib

from lodel.plugin import Plugins
from lodel import logger
from lodel.settings import Settings
from lodel.settings.utils import SettingsError

class LeApiErrors(Exception):
    ##@brief Instanciate a new exceptions handling multiple exceptions
    # @param msg str : Exception message
    # @param exceptions dict : A list of data check Exception with concerned field (or stuff) as key
    def __init__(self, msg = "Unknow error", exceptions = None):
        self._msg = msg
        self._exceptions = dict() if exceptions is None else exceptions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = self._msg
        for_iter = self._exceptions.items() if isinstance(self._exceptions, dict) else enumerate(self.__exceptions)
        for obj, expt in for_iter:
            msg += "\n\t{expt_obj} : ({expt_name}) {expt_msg}; ".format(
                    expt_obj = obj,
                    expt_name=expt.__class__.__name__,
                    expt_msg=str(expt)
            )
        return msg


##@brief When an error concern a query
class LeApiQueryError(LeApiErrors):
    pass


##@brief When an error concerns a datas
class LeApiDataCheckError(LeApiErrors):
    pass


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
        self.__setter = set_callback
        self.__getter = get_callback
    
    ##@brief Provide read access to datas values
    # @note Read access should be provided for all fields
    # @param fname str : Field name
    def __getattribute__(self, fname):
        return self.__getter(fname)
    
    ##@brief Provide write access to datas values
    # @note Write acces shouldn't be provided for internal or immutable fields
    # @param fname str : Field name
    # @param fval * : the field value
    def __setattribute__(self, fname, fval):
        return self.__setter(fname, fval)
        

class LeObject(object):
 
    ##@brief boolean that tells if an object is abtract or not
    _abstract = None
    ##@brief A dict that stores DataHandler instances indexed by field name
    _fields = None
    ##@brief A tuple of fieldname (or a uniq fieldname) representing uid
    _uid = None 
    ##@brief The datasource name ( see @ref lodel2_datasources )
    _datasource = None

    ##@brief Construct an object representing an Editorial component
    # @note Can be considered as EmClass instance
    def __init__(self, **kwargs):
        if self._abstract:
            raise NotImplementedError("%s is abstract, you cannot instanciate it." % self.__class__.__name__ )
        ##@brief A dict that stores fieldvalues indexed by fieldname
        self.__datas = { fname:None for fname in self._fields }
        ##@brief Store a list of initianilized fields when instanciation not complete else store True
        self.__initialized = list()
        ##@brief Datas accessor. Instance of @ref LeObjectValues
        self.d = LeObjectValues(self.fieldnames, self.set_data, self.data)

        # Checks that uid is given
        for uid_name in self._uid:
            if uid_name not in kwargs:
                raise AttributeError("Cannot instanciate a LeObject without it's identifier")
            self.__datas[uid_name] = kwargs[uid_name]
            del(kwargs[uid_name])
            self.__initialized.append(uid_name)
        
        # Processing given fields
        allowed_fieldnames = self.fieldnames(include_ro = False)
        err_list = list()
        for fieldname, fieldval in kwargs.items():
            if fieldname not in allowed_fieldnames:
                if fieldname in self._fields:
                    err_list.append(
                        AttributeError("Value given for internal field : '%s'" % fieldname)
                    )
                else:
                    err_list.append(
                        AttributeError("Unknown fieldname : '%s'" % fieldname)
                    )
            else:
                self.__datas[fieldame] = fieldval
                self.__initialized = list()
        self.set_initialized()
    
    #-----------------------------------#
    #   Fields datas handling methods   #
    #-----------------------------------#

    ##@brief @property True if LeObject is initialized else False
    @property
    def initialized(self):
        return not isinstance(self.__initialized, list)
    
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
        except AttributeError:
            raise NameError("No LeObject named '%s'" % leobject_name)
    
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
    
    ##@brief Replace the _datasource attribute value by a datasource instance
    #
    # This method is used once at dyncode load to replace the datasource string
    # by a datasource instance to avoid doing this operation for each query
    @classmethod
    def _init_datasource(cls):
        expt_msg = "In LeAPI class '%s' " % cls.__name__
        if cls._datasource not in Settings.datasources._fields:
            expt_msg += "Unknow or unconfigured datasource %s"
            expt_msg %= (cls._datasource, cls.__name__)
            raise SettingsError(expt_msg)

        ds_identifier = getattr(Settings.datasources, cls._datasource)
        try:
            ds_identifier = getattr(ds_identifier, 'identifier')
        except NameError:
            expt_msg += "Datasource %s is missconfigured, missing identifier."
            expt_msg %= cls._datasource
            raise SettingsError(expt_msg)

        ds_plugin, ds_name = ds_identifier.split('.')
        #Checks that the datasource is configured
        if ds_plugin not in Settings.datasource._fields:
            expt_msg += "Unknown or unconfigured datasource plugin %s"
            expt_msg %= ds_plugin
            raise SettingsError(expt_msg)

        ds_conf = getattr(Settings.datasource, ds_plugin)
        if ds_name not in ds_conf._fields:
            expt_msg += "Unknown or unconfigured datasource instance %s"
            expt_msg %= ds_identifier
            raise SettingsError(expt_msg)

        ds_conf = getattr(ds_conf, ds_name)
        #Checks that the datasource plugin exists
        ds_plugin_module = Plugins.plugin_module(ds_plugin)
        try:
            cls._datasource = getattr(ds_plugin_module, "Datasource")
        except AttributeError as e:
            raise e
            expt_msg += "The datasource plugin %s seems to be invalid. Error raised when trying to import Datasource"
            expt_msg %= ds_identifier
            raise SettingsError(expt_msg)
        logger.debug("Datasource initialized for LeObject %s" % cls.__name__)

    ##@brief Read only access to all datas
    # @note for fancy data accessor use @ref LeObject.g attribute @ref LeObjectValues instance
    # @param name str : field name
    # @return the Value
    # @throw RuntimeError if the field is not initialized yet
    # @throw NameError if name is not an existing field name
    def data(self, field_name):
        if field_name not in self._fields.keys():
            raise NameError("No such field in %s : %s" % (self.__class__.__name__, name))
        if not self.initialized and name not in self.__initialized:
            raise RuntimeError("The field %s is not initialized yet (and have no value)" % name)
        return self.__datas[name]
    
    ##@brief Datas setter
    # @note for fancy data accessor use @ref LeObject.g attribute @ref LeObjectValues instance
    # @param fname str : field name
    # @param fval * : field value
    # @return the value that is really set
    # @throw NameError if fname is not valid
    # @throw AttributeError if the field is not writtable
    def set_data(self, fname, fval):
        if field_name not in self.fieldnames(include_ro = False):
            if field_name not in self._fields.keys():
                raise NameError("No such field in %s : %s" % (self.__class__.__name__, name))
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
                self.__initialized = True

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
            err_l[miss_field] = AttributeError("The data for field '%s' is missing" % missing)
        #Checks datas
        checked_datas = dict()
        for name, value in [ (name, value) for name, value in datas.items() if name in correct ]:
            dh = cls._fields[name]
            res = dh.check_data_value(value)
            checked_datas[name], err = res
            if err:
                err_l[name] = err

        if len(err_l) > 0:
            raise LeApiDataCheckError("Error while checking datas", err_l)
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
            warnings.warn("\nActual implementation can make datas construction and consitency unsafe when datas are not complete\n")
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
        """
        constructor = DatasConstructor(cls, datas, cls.fieldtypes())
        ret = {
                fname:constructor[fname]
                for fname, ftype in cls.fieldtypes().items()
                if not ftype.is_internal() or ftype.internal != 'autosql'
        }
        return ret
        """
        pass

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

