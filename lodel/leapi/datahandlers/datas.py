#-*- coding: utf-8 -*-

## @package lodel.leapi.datahandlers.datas
# This module contains specific datahandlers extending the basic ones from the lodel.leapi.datahandlers.datas_base module.


import warnings
import inspect
import re

from lodel.leapi.datahandlers.datas_base import Boolean, Integer, Varchar, DateTime, Text, File
from lodel.exceptions import LodelException, LodelExceptions, LodelFatalError, DataNoneValid, FieldValidationError


## @brief Data field designed to handle formated strings
class FormatString(Varchar):

    help = 'Automatic string field, designed to use the str % operator to build its content'
    base_type = 'char'
    
    ## @brief Constructor
    # @param _field_list list : List of fields to use
    # @param _format_string str : formatted string
    # @param **kwargs : additional options
    def __init__(self, format_string, field_list, **kwargs):
        self._field_list = field_list
        self._format_string = format_string
        super().__init__(internal='automatic', **kwargs)

    ## @brief constructs the formatted string data
    # The string can be truncated depending on the maximum length defined for this field.
    #
    # @param emcomponent EmComponent
    # @param fname str
    # @param datas dict
    # @param cur_value str
    # @return str
    def _construct_data(self, emcomponent, fname, datas, cur_value):
        ret = self._format_string % tuple(
            datas[fname] for fname in self._field_list)
        if len(ret) > self.max_length:
            warnings.warn("Format field overflow. Truncating value")
            ret = ret[:self.max_length]
        return ret


## @brief Varchar validated by a regex
class Regex(Varchar):

    help = 'String field validated with a regex. Takes two options : \
max_length and regex'
    base_type = 'char'

    ## @brief A string field validated by a regex
    # @param regex str : a regex string (passed as argument to re.compile()), default value is an empty string
    # @param max_length int : the max length for this field (default : 10)
    # @param **kwargs : additional options
    def __init__(self, regex='', max_length=10, **kwargs):
        self.regex = regex
        self.compiled_re = re.compile(regex)  # trigger an error if invalid regex
        super(self.__class__, self).__init__(max_length=max_length, **kwargs)

    ## @brief Check and cast value in appropriate type
    # @param value *
    # @throw FieldValidationError if value is unappropriate or can not be cast
    # @return str
    def _check_data_value(self, value):
        value = super()._check_data_value(value)
        if not self.compiled_re.match(value) or len(value) > self.max_length:
            msg = '"%s" doesn\'t match the regex "%s"' % (value, self.regex)
            raise FieldValidationError(msg)
        return value

    ## @brief checks if another datahandler can override this one
    #
    # @param data_handler Datahandler
    # @return bool
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

    ## @brief A uid field
    #
    # @param **kwargs dict
    def __init__(self, **kwargs):
        kwargs['internal'] = 'automatic'
        super(self.__class__, self).__init__(primary_key = True, **kwargs)

    ## @brief Constructs the field's data
    # @param emcomponent EmComponent : Component corresponding to the field
    # @param fname
    # @param datas
    # @param cur_value str : current value to use (is retrieved from the datasource if not given)
    # @return str
    # @remarks fname and datas are not used and should become non mandatory, cur_value should have a None default value
    def construct_data(self, emcomponent, fname, datas, cur_value):
        if cur_value is None:
            #Ask datasource to provide a new uniqID
            return emcomponent._ro_datasource.new_numeric_id(emcomponent)
        return cur_value


## @brief Class representing a LeObject subclass
class LeobjectSubclassIdentifier(Varchar):
    
    help = 'Datahandler designed to handle LeObject subclass identifier in DB'
    base_type = 'varchar'

    ## @brief Constructor
    # @param kwargs dict : additional options
    # @throw RuntimeError
    # @todo define the "internal" option that can be given in the kwargs, and document its meaning
    def __init__(self, **kwargs):
        if 'internal' in kwargs and not kwargs['internal']:
            raise RuntimeError(self.__class__.__name__+" datahandler can only \
be internal")
        kwargs['internal'] = True
        super().__init__(**kwargs)

    ## @brief Returns the class' name
    # @param emcomponent EmComponent : Component correponding to the field
    # @param fname
    # @param datas
    # @param cur_value
    # @return str
    # @remarks fname, datas and cur_value should be given default values as they are not mandatory here.
    def construct_data(self, emcomponent, fname, datas, cur_value):
        cls = emcomponent
        if not inspect.isclass(emcomponent):
            cls = emcomponent.__class__
        return cls.__name__


## @brief Data field designed to handle concatenated fields
class Concat(FormatString):
    help = 'Automatic strings concatenation'
    base_type = 'char'
    
    ## @brief Build its content with a field list and a separator
    # @param field_list list : List of fields to concatenate
    # @param separator str
    # @param **kwargs    
    def __init__(self, field_list, separator=' ', **kwargs):
        format_string = separator.join(['%s' for _ in field_list])
        super().__init__(format_string=format_string,
                         field_list=field_list,
                         **kwargs)


## @brief Datahandler managing a password
class Password(Varchar):
    help = 'Handle passwords'
    base_type = 'password'
    pass

## @brief Datahandler turning a string into a list
class VarcharList(Varchar):
    help = 'DataHandler designed to make a list out of a string.'
    base_type = 'varchar'

    ## @brief Constructor
    # @param delimiter str : default value is a whitespace character
    # @param **kwargs : additional options
    # @throw LodelException : this exception is raised when the delimiter is not a string
    def __init__(self, delimiter=' ', **kwargs):
        if not isinstance(delimiter, str):
            raise LodelException("The delimiter has to be a string, %s given" % type(delimiter))
        self.delimiter = str(delimiter)
        super().__init__(**kwargs)

    ## @brief Constructs the field's data
    # @param emcomponent EmComponent
    # @param fname
    # @param datas
    # @param cur_value : current value to use
    # @return list
    # @remarks emcomponent, fname and datas should be given a default value as they seem to be non mandatory
    def construct_data(self, emcomponent, fname, datas, cur_value):
        result = cur_value.split(self.delimiter)
        return result
