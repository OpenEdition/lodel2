#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes.generic import GenericFieldType


class EmFieldType(GenericFieldType):

    help = 'A text field (big string)'

    ftype = 'text'

    def __init__(self, **kwargs):
        super(EmFieldType, self).__init__(ftype='text', **kwargs)

