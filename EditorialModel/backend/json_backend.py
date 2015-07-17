# -*- coding: utf-8 -*-

## @file json_backend.py
# Load representation of an EditorialModel from a json file

import json


## Manages a Json file based backend structure
class EmBackendJson(object):

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
            data[int(index)] = component
        return data
