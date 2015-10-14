#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes.generic import GenericFieldType

class EmFieldText(GenericFieldType):

    help = 'A text field (big string)'

    def __init__(self, **kwargs):
        super(EmFieldText, self).__init__(ftype='text',**kwargs)

