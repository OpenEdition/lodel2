#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes.generic import GenericFieldType

class EmFieldType(GenericFieldType):

    help = 'A datetime field. Take two boolean options now_on_update and now_on_create'

    ftype='datetime'

    ## @brief A datetime field
    # @param now_on_update bool : If true the date is set to NOW on update
    # @param now_on_create bool : If true the date is set to NEW on creation
    def __init__(self, now_on_update=False, now_on_create=False, **kwargs):
        self.now_on_update = now_on_update
        self.now_on_create = now_on_create
        super(EmFieldType, self).__init__(ftype='datetime',**kwargs)

