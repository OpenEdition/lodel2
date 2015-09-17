#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField


class EmFieldInt(EmField):
    
    ftype = 'int'

    help = 'Basic integer field'

    def __init__(self, **kwargs):
        super(EmFieldChar, self).__init__(**kwargs)

fclass=EmFieldInt
