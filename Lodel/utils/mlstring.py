# -*- coding: utf-8 -*-

import json

class MlString(object):
    """ Handle string with translations """

    def __init__(self, translations = dict()):
        self.translations = translations

    def get(self, lang):
        if not lang in self.translations:
            return ''

        return self.translations[lang]

    def set(self, lang, text):
        if not text:
            if lang in self.translations:
                del(self.translations[lang])
        else:
            self.translations[lang] = text

    def __str__(self):
        if self.translations:
            return json.dumps(self.translations)
        else:
            return ""

    def __eq__(self, other):
        if not isinstance(other, MlString):
            return False
        if not set(lng for lng in self.translations) == set( lng for lng in other.translations):
            return False
        for lng in self.translations:
            if self.get(lng) != other.get(lng):
                return False
        return True

    @staticmethod
    def load(json_string):
        if isinstance(json_string, str) and json_string != '':
            translations = json.loads(json_string)
        else:
            translations = dict()
        return MlString(translations)
