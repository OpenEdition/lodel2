# -*- coding: utf-8 -*-
from .field_data_handler import FieldDataHandler


class Relation(FieldDataHandler):

    def __init__(self):
        self.backref_fieldname=''
