#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField


class EmFieldFile(EmField):

    help = 'A file field. With one options upload_path'

    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, upload_path=None, **kwargs):
        self.upload_path = upload_path
        super(EmFieldFile, self).__init__(ftype='char',**kwargs)

