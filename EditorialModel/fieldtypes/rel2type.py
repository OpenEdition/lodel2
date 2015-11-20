#-*- coding: utf-8 -*-

from .generic import GenericFieldType
from EditorialModel.fields import EmField


class EmFieldType(GenericFieldType):

    help = 'Relationnal field (relation2type). Take rel_to_type_id as option (an EmType uid)'

    ftype = 'rel2type'

    def __init__(self, rel_to_type_id, **kwargs):
        self.rel_to_type_id = rel_to_type_id
        super(EmFieldType, self).__init__(ftype='rel2type', **kwargs)

    def get_related_type(self):
        return self.model.component(self.rel_to_type_id)

    def get_related_fields(self):
        return [f for f in self.model.components(EmField) if f.rel_field_id == self.uid]
