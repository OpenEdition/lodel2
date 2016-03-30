# -*- coding: utf-8 -*-
from .integer import EmDataField as IntegerDataField


class DataHandler(IntegerDataField):

    help = 'Fieldtype designed to handle editorial model UID'
    base_type = 'int'

    ## @brief A uid field
    # @param **kwargs
    def __init__(self, is_id_class, **kwargs):
        self._is_id_class = is_id_class
        kwargs['internal'] = 'automatic'
        super(self.__class__, self).__init__(is_id_class=is_id_class, **kwargs)

    def _check_data_value(self, value):
        return (value, None)

    def can_override(self,data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False

        return True