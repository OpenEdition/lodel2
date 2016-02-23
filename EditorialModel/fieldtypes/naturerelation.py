#-*- coding: utf-8 -*-

from . import char

import EditorialModel.classtypes as classtypes
import leapi.lerelation as lerelation

class EmFieldType(char.EmFieldType):
    
    help = 'Stores a relation\'s nature'

    def __init__(self, **kwargs):
        kwargs.update({'nullable': True})
        super().__init__(**kwargs)

    def _check_data_value(self, value):
        if value is None or ( value in classtypes.EmNature.getall()):
            return value, None
        else:
            return None, ValueError("Unknown relation nature '%s'"%value)
    
    ## @todo implements types checks
    def check_data_consistency(self, lec, fname, datas):
        #Checking given component
        #Replace with a test from _LeCrud
        #if not isinstance(lec, lerelation._LeRelation):
        #    return ValueError("A field naturerelation has to be in a LeRelation object, but this one is in a '%s'"%lec.__name__)
        nature = datas[fname]
        lesup = datas[lec._superior_field_name]
        lesub = datas[lec._subordinate_field_name]
        if nature is None:
            #if not isinstance(lec, lerelation.LeRel2Type):
            #Replace with a test from _LeCrud
            #    return ValueError("Only LeRel2Type are allowed to have NULL nature")
            pass
        else:
            #if not isinstance(lec, lerelation.LeHierarch):
            #Replace with a test from _LeCrud
            #    return ValueError("Only LeHierarch has not NULL nature")
            #Checking if nature <=> lesup & lesub classtypes
            if not lesub.is_partial():
                if nature not in classtypes.EmClassType.natures(lesub._classtype):
                    return ValueError("Invalid nature '%s' for %s"%(nature, lesub.__class__.__name__))
            
            if not lesup.is_partial() and not lesup.is_root():
                if nature not in classtypes.EmClassType.natures(lesup._classtype):
                    return ValueError("Invalid nature '%s' for %s"%(nature, lesup.__class__.__name__))
        return True
