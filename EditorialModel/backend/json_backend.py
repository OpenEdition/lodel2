# -*- coding: utf-8 -*-

## @package EditorialModel.backend.json_backend
# @brief Handle json files
# 
# Allows an editorial model to be loaded/saved in
# json format

import json
import datetime
from Lodel.utils.mlstring import MlString
import EditorialModel


def date_cast(date):
    if len(date):
        return datetime.datetime.strptime(date, '%c')
    else:
        return None


## @brief dirty obsolote cast function
def int_or_none(i):
    if isinstance(i, int):
        return i
    elif i is None:
        return None
    elif len(i):
        return int(i)
    else:
        return None


## Manages a Json file based backend structure
class EmBackendJson(object):

    cast_methods = {
        'uid': int,
        'rank': int,
        'class_id': int,
        'fieldgroup_id': int,
        'rel_to_type_id': int_or_none,
        'rel_field_id': int_or_none,
        'optional': bool,
        'internal': bool,
        'string': MlString.load,
        'help_text': MlString.load,
        'date_create': date_cast,
        'date_update': date_cast,
    }

    ## Constructor
    #
    # @param json_file str: path to the json_file used as data source
    def __init__(self, json_file):
        self.json_file = json_file
        pass

    @staticmethod
    ## @brief Used by json.dumps to serialize date and datetime
    def date_handler(obj):
        return obj.strftime('%c') if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) else None


    ## Loads the data in the data source json file
    #
    # @return list
    def load(self):
        data = {}
        with open(self.json_file) as json_data:
            rdata = json.loads(json_data.read())
            for index, component in rdata.items():
                attributes = {}
                for attr_name, attr_value in component.items():
                    if attr_name in EmBackendJson.cast_methods:
                        attributes[attr_name] = EmBackendJson.cast_methods[attr_name](attr_value)
                    else:
                        attributes[attr_name] = attr_value
                data[int(index)] = attributes
        return data

    ## Saves the data in the data source json file
    # @param filename str : The filename to save the EM in (if None use self.json_file provided at init )
    def save(self, em, filename = None):
        with open(self.json_file if filename is None else filename, 'w') as fp:
            fp.write(json.dumps({ component.uid : component.attr_flat() for component in em.components() }, default=self.date_handler))

