#-*- coding: utf-8 -*-

from .generic import GenericFieldType

class EmFieldType(GenericFieldType):
    
    help = 'Fieldtypes designed to handle pk of LeObject in LeRelations'

    ftype = 'leobject'

    def __init__(self, superior=True, **kwargs):
        super(EmFieldType, self).__init__(ftype = 'leobject', **kwargs)

    def _check_data_value(self, value):
        import leapi.lecrud as lecrud
        err = None
        if not isinstance(value, int):
            if not isinstance(value, lecrud._LeCrud.name2class('LeType')):
                return (None, ValueError("An instance of a child class of LeType was expected"))
            if not hasattr(value, 'lodel_id'):
                return (None, ValueError("The LeType instance given has no lodel_id !"))
        return (value, None)
    
    ## @brief If field value is an integer, returns a partially instanciated LeObject (only with an ID)
    def construct_data(self, lec, fname, datas):
        import leapi.lecrud as lecrud
        if isinstance(datas[fname], int):
            leobject = lecrud._LeCrud.name2class('LeObject')
            return leobject.get(datas[fname])
        else:
            return datas[fname]
    
    def check_data_consistency(self, lec, fname, datas):
        if self.superior:
            return self.check_sup_consistency()
        else:
            return self.check_sub_consistency()

    def check_sup_consistency(self, lec, fname, datas):
        pass

    def check_sub_consistency(self, lec, fname, datas):
        pass
