#-*- coding: utf-8 -*-

from lodel.leapi.datahandlers.datas_base import *

## @brief Data field designed to handle formated strings
class FormatString(Varchar):

    help = 'Automatic string field, designed to use the str % operator to build its content'
    base_type = 'char'

    ## @brief Build its content with a field list and a format string
    # @param format_string str
    # @param max_length int : the maximum length of the handled value
    # @param field_list list : List of field to use
    # @param **kwargs
    def __init__(self, format_string, field_list, max_length, **kwargs):
        self._field_list = field_list
        self._format_string = format_string
        super().__init__(internal='automatic', max_length=max_length)


    def can_override(self, data_handler):
        if not super().can_override(data_handler):
            return False
        if data_handler.max_length != self.max_length:
            return False
        return True

## @brief Varchar validated by a regex
class Regex(Varchar):

    help = 'String field validated with a regex. Takes two options : max_length and regex'
    base_type = 'char'

    ## @brief A string field validated by a regex
    # @param regex str : a regex string (passed as argument to re.compile())
    # @param max_length int : the max length for this field (default : 10)
    # @param **kwargs
    def __init__(self, regex='', max_length=10, **kwargs):
        self.regex = regex
        self.compiled_re = re.compile(regex)  # trigger an error if invalid regex

        super(self.__class__, self).__init__(max_length=max_length, **kwargs)

    def _check_data_value(self, value):
        error = None
        if not self.compiled_re.match(value):
            value = ''
            error = TypeError('"%s" doesn\'t match the regex "%s"' % (value, self.regex))
        return value, error

    def can_override(self, data_handler):
        if not super().can_override(data_handler):
            return False

        if data_handler.max_length != self.max_length:
            return False
        return True

## @brief Handles uniq ID
class UniqID(Integer):

    help = 'Fieldtype designed to handle editorial model UID'
    base_type = 'int'

    ## @brief A uid field
    # @param **kwargs
    def __init__(self, **kwargs):
        kwargs['internal'] = 'automatic'
        super(self.__class__, self).__init__(primary_key = True, **kwargs)

    def _check_data_value(self, value):
        return value, None
