#-*- coding: utf-8 -*-

from .char import EmFieldType

import EditorialModel.classtypes as classtypes
import leapi.lerelation as lerelation

class EmFieldType(EmFieldType):
    
    help = 'Stores a relation\'s nature'

    def __init__(self, **kwargs):
        kwargs.update({'nullable': True, 'check_data_value': EmFieldType.check_data_value})
        super(EmFieldType, self).__init__(**kwargs)

    def check_data_value(self, value):
        return value is None or ( value in classtypes.getall())

    def check_data_consistency(self, lec, fname, datas):
        #Checking given component
        if not isinstance(lec, lerelation.LeRelation):
            return ValueError("A field naturerelation has to be in a LeRelation object, but this one is in a '%s'"%lec.__name__)
        nature = datas[fname]
        lesup = datas['lesup']
        lesub = datas['lesub']
        if nature is None:
            if not isinstance(lec, lerelation.LeRel2Type):
                return ValueError("Only LeRel2Type are allowed to have NULL nature")
        else:
            if not isinstance(lec, lerelation.LeHierarch):
                return ValueError("Only LeHierarch has not NULL nature")
            #Checking if nature <=> lesup & lesub classtypes
            if nature not in classtypes.EmClassType.natures(lesub._classtype):
                return ValueError("Invalid nature '%s' for %s"%(nature, lesub.__class__.__name__))

            if not lesup.is_root():
                if nature not in classtypes.EmClassType.natures(lesup._classtype):
                    return ValueError("Invalid nature '%s' for %s"%(nature, lesup.__class__.__name__))
        return True
