#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes.generic import GenericFieldType

class EmFieldRel2Type(GenericFieldType):

    help = 'Relationnal field (relation2type). Take rel_to_type_id as option (an EmType uid)'

    def __init__(self, rel_to_type_id, **kwargs):
        self.rel_to_type_id = rel_to_type_id
        super(EmFieldRel2Type, self).__init__(ftype='rel2type',**kwargs)

    def get_related_type(self):
        return self.model.component(self.rel_to_type_id)

    def get_related_fields(self):
        return [f for f in self.model.components(EmField) if f.rel_field_id == self.uid]

