#-*- coding: utf-8 -*-

import EditorialModel

class EmFieldType(EditorialModel.fieldtypes.integer.EmFieldType):
    
    help = 'Integer primary key fieldtype'

    def __init__(self):
        super(EmFieldType, self).__init__(ftype='int', primary=True)
