#-*- coding utf-8 -*-

import EditorialModel.classtypes
import leapi.lerelation as lerelation

from .generic import FieldTypeError
from . import integer

class EmFieldType(integer.EmFieldType):
    
    help = 'Fieldtype designed to handle relations rank'

    _construct_datas_deps = [EditorialModel.classtypes.relation_superior]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct_data(self, lec, fname, datas, cur_value):
        superior_id = datas[EditorialModel.classtypes.relation_superior]
        if lec.is_lerel2type():
            subordinate = lec._subordinate_cls
            sub_em_type_id = subordinate._type_id
            cur_value = lec.get_max_rank(superior_id, sub_em_type_id)
        elif lec.is_lehierarch():
            cur_value = lec.get_max_rank(superior_id, datas['nature'])
        else:
            raise ValueError("Called with bad class : ", lec.__name__)
        return cur_value
