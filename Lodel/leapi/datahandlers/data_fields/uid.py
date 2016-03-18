# -*- coding: utf-8 -*-
from .integer import Integer


class Uid(Integer):

    help = 'Fieldtype designed to handle editorial model UID'

    ## @brief A uid field
    # @param **kwargs
    def __init__(self, is_id_class, **kwargs):
        self._is_id_class = is_id_class
        kwargs['internal'] = 'automatic'
        super().__init__(is_id_class=is_id_class, **kwargs)

    def _check_data_value(self, value):
        return (value, None)

