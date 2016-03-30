# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldDataHandler


class DataHandler(FieldDataHandler):

    ## @brief Instanciates a Relation object
    # @param datahandler FieldDataHandler
    # @param datahandler_args dict
    # @param reference EmField
    # @param kwargs
    def __init__(self, **kwargs):
        # Data Handler
        data_handler = kwargs['data_handler_kwargs']['data_handler']
        data_handler_args = kwargs['data_handler_kwargs']
        data_handler_class = FieldDataHandler.from_name(data_handler)
        self.data_handler = data_handler_class(**data_handler_args)

        # Reference
        self.backref_ref = kwargs['data_handler_kwargs']['backreference']

        super().__init__(**kwargs)
