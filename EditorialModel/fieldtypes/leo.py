#-*- coding: utf-8 -*-

import leapi.letype as letype
import leapi.leclass as leclass

from .generic import ReferenceFieldType, FieldTypeError

class EmFieldType(ReferenceFieldType):
    
    help = 'Fieldtypes designed to handle pk of LeObject in LeRelations'

    ftype = 'leobject'
    
    ## @todo Replace hardcoded string for reference initialisation
    def __init__(self, superior=True, **kwargs):
        super().__init__(superior = superior, reference='object', **kwargs)

    def _check_data_value(self, value):
        if not isinstance(value, int):
            if not letype._LeType.implements_leobject():
                return (None, ValueError("An instance of a child class of LeType was expected"))
            if not hasattr(value, 'lodel_id'):
                return (None, ValueError("The LeType instance given has no lodel_id !"))
        return (value, None)
    
    ## @brief If field value is an integer, returns a partially instanciated LeObject (only with an ID)
    # @todo what should we do if the get fails ? Raise ?
    def construct_data(self, lec, fname, datas):
        if isinstance(datas[fname], str):
            # Cast to int
            try:
                datas[fname] = int(datas[fname])
            except (ValueError, TypeError) as e:
                raise e # Raise Here !?
        if datas[fname].is_leobject():
            # Its an object not populated (we dont now its type)
            datas[fname] = datas[fname].lodel_id #Optimize here giving only class_id and type_id to populate ?
        if isinstance(datas[fname], int):
            # Get instance with id
            resget = lec.name2class('LeObject').get(['lodel_id = %d' % datas[fname]])
            if resget is None or len(resget) != 1:
                # Bad filter or bad id... raise ?
                raise Exception("BAAAAAD")
        return datas[fname]
    
    ## @brief checks datas consistency
    # @param lec LeCrud : A LeCrud child instance
    # @param fname str : concerned field name
    # @param datas dict : Datas of lec
    # @return True if ok else an Exception instance
    def check_data_consistency(self, lec, fname, datas):
        if self.superior:
            return self.check_sup_consistency(lec, fname, datas)
        else:
            return self.check_sub_consistency(lec, fname, datas)

    def check_sup_consistency(self, lec, fname, datas):
        if lec.implements_lerel2type():
            # Checking consistency for a rel2type relation
            lesup = datas[lec._superior_field_name]
            lesub = datas[lec._subordinate_field_name]
            if lesub.__class__ not in lesup._linked_types:
                return FieldTypeError("Rel2type not authorized between %s and %s"%(lesup, lesub))
        pass
            

    def check_sub_consistency(self, lec, fname, datas):
        pass
