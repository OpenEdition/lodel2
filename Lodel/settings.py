#-*- coding: utf-8 -*-

import settings_local

class Settings:
    # List of accepted settings
    datasource = None

    @staticmethod
    # @throw AttributeError if the setting is not defined in this class
    def get(attribute):
        value = None
        # find the value in settings itself, if not set search in settings_local
        value = getattr(Settings, attribute)
        if value is None:
            try:
                value = getattr(settings_local, attribute)
            except AttributeError:
                pass

        if value is not None:
            try:
                func = getattr(Settings, attribute + '_args')
                value = func(value)
            except AttributeError:
                pass

        return value

    @staticmethod
    # @throw AttributeError if the setting is not defined in this class
    def set(attribute, value):
        setattr(Settings, attribute, value)

    @staticmethod
    def datasource_args(value):
        return value