#-*- coding: utf-8 -*-

import importlib

class LeApiErrors(Exception):
    ## @brief Instanciate a new exceptions handling multiple exceptions
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


## @brief When an error concern a query
class LeApiQueryError(LeApiErrors):
    pass


## @brief When an error concerns a datas
class LeApiDataCheckError(LeApiErrors):
    pass


## @brief Wrapper class for LeObject getter & setter
#
# This class intend to provide easy & friendly access to LeObject fields values 
# without name collision problems
# @note Wrapped methods are : LeObject.data() & LeObject.set_data()
class LeObjectValues(object):
    
    ## @brief Construct a new LeObjectValues
    # @param set_callback method : The LeObject.set_datas() method of corresponding LeObject class
    # @param get_callback method : The LeObject.get_datas() method of corresponding LeObject class
    def __init__(self, fieldnames_callback, set_callback, get_callback):
        self.__setter = set_callback
        self.__getter = get_callback
    
    ## @brief Provide read access to datas values
    # @note Read access should be provided for all fields
    # @param fname str : Field name
    def __getattribute__(self, fname):
        return self.__getter(fname)
    
    ## @brief Provide write access to datas values
    # @note Write acces shouldn't be provided for internal or immutable fields
    # @param fname str : Field name
    # @param fval * : the field value
    def __setattribute__(self, fname, fval):
        return self.__setter(fname, fval)
        

class LeObject(object):
 
    ## @brief boolean that tells if an object is abtract or not
    _abstract = None
    ## @brief A dict that stores DataHandler instances indexed by field name
    _fields = None
    ## @brief A tuple of fieldname (or a uniq fieldname) representing uid
    _uid = None 

    ## @brief Construct an object representing an Editorial component
    # @note Can be considered as EmClass instance
    def __init__(self, **kwargs):
        if self._abstract:
            raise NotImplementedError("%s is abstract, you cannot instanciate it." % self.__class__.__name__ )
        ## @brief A dict that stores fieldvalues indexed by fieldname
        self.__datas = { fname:None for fname in self._fields }
        ## @brief Store a list of initianilized fields when instanciation not complete else store True
        self.__initialized = list()
        ## @brief Datas accessor. Instance of @ref LeObjectValues
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

    ## @brief @property True if LeObject is initialized else False
    @property
    def initialized(self):
        return not isinstance(self.__initialized, list)

    ## @brief Return a list of fieldnames
    # @param include_ro bool : if True include read only field names
    # @return a list of str
    @classmethod
    def fieldnames(cls, include_ro = False):
        if not include_ro:
            return [ fname for fname in self._fields if not self._fields[fname].is_internal() ]
        else:
            return list(self._fields.keys())
 
    @classmethod
    def name2objname(cls, name):
        return name.title()
    
    ## @brief Return the datahandler asssociated with a LeObject field
    # @param fieldname str : The fieldname
    # @return A data handler instance
    @classmethod
    def data_handler(cls, fieldname):
        if not fieldname in cls._fields:
            raise NameError("No field named '%s' in %s" % (fieldname, cls.__name__))
        return cls._fields[fieldname]
 
    ## @brief Return a LeObject child class from a name
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
    
    ## @brief Method designed to "bootstrap" fields by settings their back references
    # 
    # @note called once at dyncode load
    # @note doesn't do any consistency checks, it assume that checks has been done EM side
    # @warning after dyncode load this method is deleted
    @classmethod
    def _backref_init(cls):
        for fname,field in cls._fields.items():
            #if field.is_reference():
            #    print(fname, field.back_reference)
            if field.is_reference() and field.back_reference is not None:
                cls_name, field_name = field.back_reference
                bref_leobject = cls.name2class(cls.name2objname(cls_name))
                if field_name not in bref_leobject._fields:
                    raise NameError("LeObject %s doesn't have a field named '%s'" % (cls_name, field_name))
                field._set_back_reference(bref_leobject._fields[field_name])

    @classmethod
    def is_abstract(cls):
        return cls._abstract

    ## @brief Read only access to all datas
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
    
    ## @brief Datas setter
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
    
    ## @brief Update the __initialized attribute according to LeObject internal state
    #
    # Check the list of initialized fields and set __initialized to True if all fields initialized
    def __set_initialized(self):
        if isinstance(self.__initialized, list):
            expected_fields = self.fieldnames(include_ro = False) + self._uid
            if set(expected_fields) == set(self.__initialized):
                self.__initialized = True

    ## @brief Designed to be called when datas are modified
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
    
    ## @brief Temporary method to set private fields attribute at dynamic code generation
    #
    # This method is used in the generated dynamic code to set the _fields attribute
    # at the end of the dyncode parse
    # @warning This method is deleted once the dynamic code loaded
    # @param field_list list : list of EmField instance
    @classmethod
    def _set__fields(cls, field_list):
        cls._fields = field_list
        


    
