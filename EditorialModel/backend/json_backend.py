# -*- coding: utf-8 -*-

## @package EditorialModel.backend.json_backend
# @brief Handle json files
#
# Allows an editorial model to be loaded/saved in
# json format

import json
import datetime
from Lodel.utils.mlstring import MlString
from EditorialModel.backend.dummy_backend import EmBackendDummy


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
class EmBackendJson(EmBackendDummy):

    cast_methods = {
        'uid': int,
        'rank': int,
        'class_id': int,
        'fieldgroup_id': int,
        'rel_to_type_id': int_or_none,
        'rel_field_id': int_or_none,
        'optional': bool,
        'string': MlString.load,
        'help_text': MlString.load,
        'date_create': date_cast,
        'date_update': date_cast,
    }

    ## Constructor
    #
    # @param json_file str: path to the json_file used as data source
    # @param json_string str: json_data used as data source
    def __init__(self, json_file=None, json_string=None):
        if (not json_file and not json_string) or (json_file and json_string):
            raise AttributeError
        self._json_file = json_file
        self._json_string = json_string

    @staticmethod
    ## @brief Used by json.dumps to serialize date and datetime
    def date_handler(obj):
        return obj.strftime('%c') if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) else None

    ## Loads the data from given file or string
    #
    # @return list
    def load(self):
        data = {}
        json_string = self._load_from_file() if self._json_file else self._json_string
        json_data = json.loads(json_string)
        for index, component in json_data.items():
            attributes = {}
            for attr_name, attr_value in component.items():
                if attr_name in EmBackendJson.cast_methods:
                    attributes[attr_name] = EmBackendJson.cast_methods[attr_name](attr_value)
                else:
                    attributes[attr_name] = attr_value
            data[int(index)] = attributes

        return data

    def _load_from_file(self):
        with open(self._json_file) as content:
            data = content.read()
        return data

    ## Saves the data in the data source json file
    # @param model Model : The editorial model
    # @param filename str|None : The filename to save the EM in (if None use self.json_file provided at init )
    # @return json string
    def save(self, model, filename=None):
        json_dump = json.dumps({component.uid: component.attr_flat() for component in model.components()}, default=self.date_handler, indent=True)
        if self._json_file:
            with open(self._json_file if filename is None else filename, 'w') as json_file:
                json_file.write(json_dump)
        else:
            return json_dump
