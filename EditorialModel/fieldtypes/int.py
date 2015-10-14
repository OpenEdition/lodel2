#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes import GenericFieldType


class EmFieldInt(GenericFieldType):

    help = 'Basic integer field'

    def __init__(self, **kwargs):
        super(EmFieldInt, self).__init__(ftype='int',**kwargs)

fclass = EmFieldInt
