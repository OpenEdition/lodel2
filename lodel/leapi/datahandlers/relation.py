# -*- coding: utf-8 -*-
from .field_data_handler import FieldDataHandler


class Relation(FieldDataHandler):

    ## @brief Instanciates a Relation object
    # @param fieldname : the fieldname involved in the relation
    # @param reference : the reference corresponding to this relation
    # @todo ajouter la récupération des objets correspondant pour le field et la référence
    def __init__(self, fieldname, reference, **kwargs):
        self.backref_fieldname = fieldname
        self.reference = reference
        super().__init__(**kwargs)
