#-*- coding: utf-8 -*-

import re
from . import char


class EmFieldType(char.EmFieldType):

    help = 'String field validated with a regex. Take two options : max_length and regex'

    ## @brief A char field validated with a regex
    # @param regex str : a regex string (passed as argument to re.compile() )
    # @param max_length int : the maximum length for this field
    # @param **kwargs
    def __init__(self, regex='', max_length=10, **kwargs):
        self.regex = regex
        self.compiled_re = re.compile(regex)  # trigger an error if invalid regex


        super().__init__(check_data_value=check_value, max_length=max_length, **kwargs)

    def _check_data_value(self,value):
        error = None
        if not self.compiled_re.match(value):
            value = ''
            error = TypeError('"%s" don\'t match the regex "%s"' % (value, self.regex))
        return (value, error)
