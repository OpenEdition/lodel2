# -*- coding: utf-8 -*-

import json


## Handle string with translations
# @todo define a default language that will be used in case the wanted language is not available for this string (gettext-like behavior)
class MlString(object):

    ## Instanciate a new string with translation
    #
    # @param translations dict: With key = lang and value the translation
    def __init__(self, translations=None):
        self.translations = dict() if translations is None else translations
    
    ## Return a translation
    # @param lang str: The lang
    # @return An empty string if the wanted lang don't exist
    # @warning Returns an empty string if the wanted translation didn't exists
    # @todo if the asked language is not available, use the default one, defined as a class property
    def get(self, lang):
        if not lang in self.translations:
            return ''

        return self.translations[lang]
    
    ## Set a translation for this MlString
    # @param lang str: The language
    # @param text str: The translation
    # @todo check if the default language as a translation
    def set(self, lang, text):
        if not text:
            if lang in self.translations:
                del(self.translations[lang])
        else:
            self.translations[lang] = text
    ## String representation
    # @return A json dump of the MlString::translations dict
    def __str__(self):
        if self.translations:
            return json.dumps(self.translations, sort_keys=True)
        else:
            return ""

    ## Test if two MlString instance are equivalent
    # @param other MlString|str : Another MlString instance or a string (json formated)
    # @return True or False
    def __eq__(self, other):
        if isinstance(other, str):
            other = MlString.load(other)

        if not isinstance(other, MlString):
            return False
        if not set(lng for lng in self.translations) == set( lng for lng in other.translations):
            return False
        for lng in self.translations:
            if self.get(lng) != other.get(lng):
                return False
        return True

    @staticmethod
    ## Instanciate a MlString from json
    # @param json_string str: Json datas in a string
    # @return A new MlString instance
    # @warning fails silently
    def load(json_string):
        if isinstance(json_string, str) and json_string != '':
            translations = json.loads(json_string)
        else:
            translations = dict()
        return MlString(translations)
