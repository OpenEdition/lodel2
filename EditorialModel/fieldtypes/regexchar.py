#-*- coding: utf-8 -*-

import re
import EditorialModel.fieldtypes.char.EmFieldType

class EmFieldType(EditorialModel.fieldtypes.char.EmFieldType):

    help = 'String field validated with a regex. Take two optionss : max_length and regex'

    ## @brief A char field validated with a regex
    # @param regex str : a regex string (passed as argument to re.compile() )
    # @param max_length int : the maximum length for this field
    def __init__(self, regex='', **kwargs):
        self.regex = regex
        v_re = re.compile(regex)  # trigger an error if invalid regex
        
        def re_match(value):
            if not v_re.match(regex, value):
                raise TypeError('"%s" don\'t match the regex "%s"'%(value, regex))
        super(EmFieldType, self).__init__(check_function=re_match,**kwargs)

