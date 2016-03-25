# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldDataHandler
from lodel.editorial_model.components import EmField


class Relation(FieldDataHandler):

    ## @brief Instanciates a Relation object
    # @param datahandler FieldDataHandler
    # @param datahandler_args dict
    # @param reference Reference
    # @param kwargs
    def __init__(self, datahandler, datahandler_args, reference, **kwargs):
        # TODO uid ?
        self.backref_field = EmField(data_handler=datahandler, **datahandler_args)
        self.backref_ref = reference
        super().__init__(**kwargs)

    def _check_data_value(self, value):
        pass

    def construct_data(self, emcomponent, fname, datas, cur_value):
        pass