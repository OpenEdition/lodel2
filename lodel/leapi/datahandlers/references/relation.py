# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldDataHandler


class DataHandler(FieldDataHandler):

    ## @brief Instanciates a Relation object
    # @param datahandler FieldDataHandler
    # @param datahandler_args dict
    # @param reference EmField
    # @param kwargs
    def __init__(self, datahandler, datahandler_args, reference, **kwargs):

        # Data Handler
        data_handler_class = FieldDataHandler.from_name(datahandler)
        self.data_handler = data_handler_class(**datahandler_args)

        # Reference
        self.backref_ref = reference

        super().__init__(**kwargs)
