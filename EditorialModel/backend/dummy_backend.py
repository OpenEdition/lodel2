# -*- coding: utf-8 -*-

## @package EditorialModel.backend.dummy_backend
# @brief Gives an empty backend
#
# Allows an editorial model to use an empty backend
# Mostly for migration and test purpose

## Manages a Json file based backend structure
class EmBackendDummy(object):

    def load(self):
        data = {}
        return data

    def save(self):
        return True
