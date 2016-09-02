#-*- coding: utf-8 -*-
import warnings
import inspect
from lodel.leapi.datahandlers.datas_base import *
from lodel.leapi.datahandlers.base_classes import FieldValidationError
import re

##@brief Data field designed to handle formated strings
class FormatString(Varchar):

    help = 'Automatic string field, designed to use the str % operator to \
build its content'
    base_type = 'char'
    
    ##@brief Build its content with a field list and a format string
    # @param format_string str
    # @param max_length int : the maximum length of the handled value
    # @param field_list list : List of field to use
    # @param **kwargs
    def __init__(self, format_string, field_list, **kwargs):
        self._field_list = field_list
        self._format_string = format_string
        super().__init__(internal='automatic',**kwargs)

    def _construct_data(self, emcomponent, fname, datas, cur_value):
        ret = self._format_string % tuple(
            datas[fname] for fname in self._field_list)
        if len(ret) > self.max_length:
            warnings.warn("Format field overflow. Truncating value")
            ret = ret[:self.max_length]
        return ret
    
##@brief Varchar validated by a regex
class Regex(Varchar):

    help = 'String field validated with a regex. Takes two options : \
max_length and regex'
    base_type = 'char'

    ##@brief A string field validated by a regex
    # @param regex str : a regex string (passed as argument to re.compile())
    # @param max_length int : the max length for this field (default : 10)
    # @param **kwargs
    def __init__(self, regex='', max_length=10, **kwargs):
        self.regex = regex
        self.compiled_re = re.compile(regex)#trigger an error if invalid regex
        super(self.__class__, self).__init__(max_length=max_length, **kwargs)

    def _check_data_value(self, value):
        value = super()._check_data_value(value)
        if not self.compiled_re.match(value) or len(value) > self.max_length:
            msg = '"%s" doesn\'t match the regex "%s"' % (value, self.regex)
            raise FieldValidationError(msg)
        return value

    def can_override(self, data_handler):
        if not super().can_override(data_handler):
            return False

        if data_handler.max_length != self.max_length:
            return False
        return True

##@brief Handles uniq ID
class UniqID(Integer):

    help = 'Fieldtype designed to handle editorial model UID'
    base_type = 'int'

    ##@brief A uid field
    # @param **kwargs
    def __init__(self, **kwargs):
        kwargs['internal'] = 'automatic'
        super(self.__class__, self).__init__(primary_key = True, **kwargs)

    def construct_data(self, emcomponent, fname, datas, cur_value):
        if cur_value is None:
            #Ask datasource to provide a new uniqID
            return emcomponent._ro_datasource.new_numeric_id(emcomponent)
        return cur_value

class LeobjectSubclassIdentifier(Varchar):
    
    help = 'Datahandler designed to handle LeObject subclass identifier in DB'
    base_type = 'varchar'

    def __init__(self, **kwargs):
        if 'internal' in kwargs and not kwargs['internal']:
            raise RuntimeError(self.__class__.__name__+" datahandler can only \
be internal")
        kwargs['internal'] = True
        super().__init__(**kwargs)
    
    def construct_data(self, emcomponent, fname, datas, cur_value):
        cls = emcomponent
        if not inspect.isclass(emcomponent):
            cls = emcomponent.__class__
        return cls.__name__
        
##@brief Data field designed to handle concatenated fields
class Concat(FormatString):
    help = 'Automatic strings concatenation'
    base_type = 'char'
    
    ##@brief Build its content with a field list and a separator
    # @param field_list list : List of field to use
    # @param max_length int : the maximum length of the handled value
    # @param separator str
    # @param **kwargs    
    def __init__(self, field_list, separator = ' ', **kwargs):
        format_string = separator.join(['%s' for _ in field_list])
        super().__init__(
            format_string = format_string, field_list = field_list, **kwargs)

class Password(Varchar):
    help = 'Handle passwords'
    base_type = 'password'
    pass
