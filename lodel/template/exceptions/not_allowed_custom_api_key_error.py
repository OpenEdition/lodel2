#-*- coding: utf-8 -*-


class NotAllowedCustomAPIKeyError(Exception):

    def __init__(self, message):
        self.message = message
