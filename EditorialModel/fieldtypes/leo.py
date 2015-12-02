#-*- coding: utf-8 -*-

import leapi.letype as letype
import leapi.leclass as leclass

from .generic import GenericFieldType

class EmFieldType(GenericFieldType):
    
    help = 'Fieldtypes designed to handle pk of LeObject in LeRelations'

    ftype = 'leobject'

    def __init__(self, superior=True, **kwargs):
        super(EmFieldType, self).__init__(ftype = 'leobject', superior = superior, **kwargs)

    def _check_data_value(self, value):
        err = None
        if not isinstance(value, int):
            if not letype._LeType.implements_leobject():
                return (None, ValueError("An instance of a child class of LeType was expected"))
            if not hasattr(value, 'lodel_id'):
                return (None, ValueError("The LeType instance given has no lodel_id !"))
        return (value, None)
    
    ## @brief If field value is an integer, returns a partially instanciated LeObject (only with an ID)
    def construct_data(self, lec, fname, datas):
        if isinstance(datas[fname], int):
            leobject = lec.name2class('LeObject')
            return leobject(datas[fname])
        else:
            return datas[fname]
    
    def check_data_consistency(self, lec, fname, datas):
        if self.superior:
            return self.check_sup_consistency(lec, fname, datas)
        else:
            return self.check_sub_consistency(lec, fname, datas)

    def check_sup_consistency(self, lec, fname, datas):
        pass

    def check_sub_consistency(self, lec, fname, datas):
        pass
