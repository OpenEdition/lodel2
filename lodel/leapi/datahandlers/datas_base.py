#-*- coding: utf-8 -*-
import warnings
import datetime

from lodel.leapi.datahandlers.base_classes import DataField

##@brief Data field designed to handle boolean values
class Boolean(DataField):

    help = 'A basic boolean field'
    base_type = 'bool'

    ##@brief A boolean field
    def __init__(self, **kwargs):
        if 'check_data_value' not in kwargs:
            kwargs['check_data_value'] = self.check_data_value
        super().__init__(ftype='bool', **kwargs)

    def _check_data_value(self, value):
        error = None
        try:
            if type(value) != bool:
                raise TypeError()
        except(ValueError, TypeError):
            error = TypeError("The value '%s' is not, and will never, be a boolean" % value)
        return value, error

##@brief Data field designed to handle integer values
class Integer(DataField):

    help = 'Basic integer field'
    base_type = 'int'

    def __init__(self, **kwargs):
        super().__init__( **kwargs)

    def _check_data_value(self, value):
        error = None
        try:
            value = int(value)
        except(ValueError, TypeError):
            error = TypeError("The value '%s' is not, and will never, be an integer" % value)
        return value, error

##@brief Data field designed to handle string
class Varchar(DataField):

    help = 'Basic string (varchar) field. Default size is 64 characters'
    base_type = 'char'

    ##@brief A string field
    # @brief max_length int: The maximum length of this field
    def __init__(self, max_length=64, **kwargs):
        self.max_length = int(max_length)
        super().__init__(**kwargs)

    ##@brief checks if this class can override the given data handler
    # @param data_handler DataHandler
    # @return bool
    def can_override(self, data_handler):
        if not super().can_override(data_handler):
            return False
        if data_handler.max_length != self.max_length:
            return False
        return True
    
    def _check_data_value(self, value):
        error = None
        try:
            value = str(value)
        except(ValueError, TypeError):
            error = TypeError("The value '%s' can't be a str" % value)
        return value, error

##@brief Data field designed to handle date & time 
class DateTime(DataField):

    help = 'A datetime field. Take two boolean options now_on_update and now_on_create'
    base_type = 'datetime'

    ##@brief A datetime field
    # @param now_on_update bool : If true, the date is set to NOW on update
    # @param now_on_create bool : If true, the date is set to NEW on creation
    # @param **kwargs
    def __init__(self, now_on_update=False, now_on_create=False, **kwargs):
        self.now_on_update = now_on_update
        self.now_on_create = now_on_create
        super().__init__(**kwargs)

    def _check_data_value(self, value):
        error = None
        return value, error

    def construct_data(self, emcomponent, fname, datas, cur_value):
        if (self.now_on_create and cur_value is None) or self.now_on_update:
            return datetime.datetime.now()
        return cur_value

##@brief Data field designed to handle long string
class Text(DataField):
    help = 'A text field (big string)'
    base_type = 'text'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(ftype='text', **kwargs)
    
    def _check_data_value(self, value):
        error = None
        return value, error

##@brief Data field designed to handle Files
class File(DataField):

    base_type = 'file'

    ##@brief a file field
    # @param upload_path str : None by default
    # @param **kwargs
    def __init__(self, upload_path=None, **kwargs):
        self.upload_path = upload_path
        super().__init__(**kwargs)
        
    def _check_data_value(self, value):
        error = None
        return value, error

