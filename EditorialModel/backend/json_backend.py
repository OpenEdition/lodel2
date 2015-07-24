# -*- coding: utf-8 -*-

## @file json_backend.py
# Load representation of an EditorialModel from a json file

import json
import datetime
from Lodel.utils.mlstring import MlString

def date_cast(date):
    if len(date):
        return datetime.datetime(date)
    else:
        return None

def int_or_none(i):
    if len(i):
        return int(i)
    else:
        return None

## Manages a Json file based backend structure
class EmBackendJson(object):

    cast_methods = {
        'uid' : int,
        'rank' : int,
        'class_id' : int,
        'fieldgroup_id' : int,
        'rel_to_type_id' : int_or_none,
        'rel_field_id' : int_or_none,
        'optional' : bool,
        'internal': bool,
        'string' : MlString.load,
        'help_text' : MlString.load,
        'date_create' : date_cast,
        'date_update' : date_cast,
    }

        

    ## Constructor
    #
    # @param json_file str: path to the json_file used as data source
    def __init__(self, json_file):
        json_data = open(json_file).read()
        self.data = json.loads(json_data)

    ## Loads the data in the data source json file
    #
    # @return list
    def load(self):
        data = {}
        for index, component in self.data.items():
            attributes = {}
            for attr_name, attr_value in component.items():
                if attr_name in EmBackendJson.cast_methods:
                    attributes[attr_name] = EmBackendJson.cast_methods[attr_name](attr_value)
                else:
                    attributes[attr_name] = attr_value
            data[int(index)] = attributes
        return data
