#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField

class EmFieldChar(EmField):
    
    ftype = 'char'

    def __init__(self, max_length=64, **kwargs):
        self.max_length = max_length
        super(EmFieldChar, self).__init__(**kwargs)

fclass = EmFieldChar
