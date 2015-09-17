#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField

class EmFieldRel2Type(EmField):

    ftype= 'rel2type'

    def __init__(self, rel_to_type_id, **kwargs):
        self.rel_to_type_id = rel_to_type_id
        super(EmFieldRel2Type, self).__init__(**kwargs)

    def get_related_type(self):
        return self.model.component(self.rel_to_type_id)

    def get_related_fields(self):
        return [ f for f in self.model.components(EmField) if f.rel_field_id == self.uid ]
        

fclass = EmFieldRel2Type
