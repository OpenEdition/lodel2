# -*- coding: utf-8 -*-

## @file json.py
# Load representation of an EditorialModel from a json file

import json

class EmBackendJson(object):

    def __init__(self, json_file):
        json_data = open(json_file).read()
        self.data = json.loads(json_data)

    def load(self):
        data = {}
        for index, component in self.data.items():
            data[int(index)] = component
        return data
