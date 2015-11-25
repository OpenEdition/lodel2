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
        v_re = re.compile(regex)  # trigger an error if invalid regex
        
        def re_match(value):
            if not v_re.match(regex, value):
                return TypeError('"%s" don\'t match the regex "%s"' % (value, regex))
        super(EmFieldType, self).__init__(check_data_value=re_match, max_length=max_length, **kwargs)
