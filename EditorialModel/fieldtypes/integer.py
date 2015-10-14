#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes.generic import GenericFieldType


class EmFieldType(GenericFieldType):

    help = 'Basic integer field'

    def __init__(self, **kwargs):
        super(EmFieldType, self).__init__(ftype='int',**kwargs)
