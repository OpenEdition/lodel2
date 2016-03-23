# -*- coding: utf-8 -*-
from .field_data_handler import FieldDataHandler


class DataField(FieldDataHandler):

    ## @brief Instanciates a new fieldtype
    # @param nullable bool : is None allowed as value ?
    # @param uniq bool : Indicates if a field should handle a uniq value
    # @param primary bool : If true the field is a primary key
    # @param internal str|False: if False, that field is not internal. Other values cans be "autosql" or "internal"
    # @param **kwargs : Other arguments
    # @throw NotImplementedError if called from bad class
    def __init__(self, internal=False, nullable=True, uniq=False, primary=False, **kwargs):
        if self.__class__ == DataField:
            raise NotImplementedError("Abstract class")

        super().__init__(internal, **kwargs)

        self.nullable = nullable
        self.uniq = uniq
        self.primary = primary
        if 'defaults' in kwargs:
            self.default, error = self.check_data_value(kwargs['default'])
            if error:
                raise error
            del(args['default'])

    def check_data_value(self, value):
        if value is None:
            if not self.nullable:
                return (None, TypeError("'None' value but field is not nullable"))

            return (None, None)
        return super().check_data_value(value)

