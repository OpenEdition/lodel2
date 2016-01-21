#-*- coding: utf-8 -*-

from EditorialModel import classtypes as lodelconst

from . import char
from .generic import FieldTypeError

class EmFieldType(char.EmFieldType):
    help = 'Only designed to handle relation_name field value'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def check_data_consistency(self, lec, fname, datas):
        # We are in a context where lec is a LeRelation child class
        if lec.implements_lerel2type():
            superior = datas[lodelconst.relation_superior]
            if datas[fname] not in superior._linked_types.keys():
                return FieldTypeError("Bad relation_name for rel2type %s : '%s'" % (lec.__name__, datas[fname]))
        elif  (datas[fname] is not None) and len(datas[fname] > 0):
            return FieldTypeError("No relation_name allowed for hierarchical relations")
        return True
            

