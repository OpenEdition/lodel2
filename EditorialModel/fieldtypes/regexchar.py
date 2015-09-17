#-*- coding: utf-8 -*-

import re
from EditorialModel.fieldtypes import EmFieldChar

class EmFieldCharRegex(EmFieldChar):
    
    def __init__(self, regex = '', **kwargs):
        self.regex = regex
        v_re = re.compile(regex) #trigger an error if invalid regex

        super(EmFieldCharRegex, self).__init__(**kwargs)

    def validation_function(self, raise_e = None, ret_valid = None, ret_invalid = None):
        super(EmFieldChar, self).validation_function(raise_e, ret_valid, ret_invalid)

        if not raise_e is None:
            def v_fun(value):
                if not re.match(self.regex):
                    raise raise_e
        else:
            def v_fun(value):
                if not re.match(self.regex):
                    return ret_invalid
                else:
                    return ret_valid
        return v_fun
 
fclass = EmFieldCharRegex
