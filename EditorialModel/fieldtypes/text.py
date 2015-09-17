#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField

class EmFieldText(EmField):
    
    ftype = 'text'

    def __init__(self, **kwargs):
        super(EmFieldText, self).__init__(**kwargs)

fclass = EmFieldText
