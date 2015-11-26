#-*- coding: utf-8 -*-

from .char import EmFieldType

import EditorialModel.classtypes as classtypes

class EmFieldType(EmFieldType):
    
    help = 'Stores a relation\'s nature'

    def __init__(self, **kwargs):
        kwargs.update({'nullable': True, 'check_data_value': EmFieldType.check_data_value})
        super(EmFieldType, self).__init__(**kwargs)

    def check_data_value(self, value):
        return value is None or ( value in classtypes.getall())
