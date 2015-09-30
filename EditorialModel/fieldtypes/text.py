#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField


class EmFieldText(EmField):

    ftype = 'text'
    help = 'A text field (big string)'

    def __init__(self, **kwargs):
        super(EmFieldText, self).__init__(**kwargs)

fclass = EmFieldText
