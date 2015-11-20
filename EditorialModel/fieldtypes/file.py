#-*- coding: utf-8 -*-

from .generic import GenericFieldType


class EmFieldType(GenericFieldType):

    help = 'A file field. With one options upload_path'

    ftype = 'char'

    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, upload_path=None, **kwargs):
        self.upload_path = upload_path
        super(EmFieldType, self).__init__(ftype='char', max_length=512, **kwargs)
