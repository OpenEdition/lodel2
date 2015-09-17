#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField

class EmFieldFile(EmField):
    
    ftype = 'file'
    
    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, upload_path = None,**kwargs):
        self.upload_path = upload_path
        super(EmFieldChar, self).__init__(**kwargs)

fclass=EmFieldFile
