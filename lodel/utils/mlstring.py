#-*- coding: utf-8 -*-

import copy
import hashlib
import json


##@brief Stores multilangage string
class MlString(object):
    
    __default_lang = 'eng'

    langs = [
        'fre',
        'eng',
        'ger',
        'esp',
    ]

    ##@brief Create a new MlString instance
    # @param arg str | dict : Can be a json string, a string or a dict. It could be also a MlString object
    def __init__(self, arg):
        self.values = dict()
        if isinstance(arg, str):
            self.values[self.__default_lang] = arg
        elif isinstance(arg, dict):
            for lang, value in arg.items():
                if not self.lang_is_valid(lang):
                    raise ValueError('Invalid lang found in argument : "%s"' % lang)
                self.values[lang] = value
        elif isinstance(arg, MlString):
            self.values = copy.copy(arg.values)
        else:
            raise ValueError('<class str>, <class dict> or <class MlString> expected, but %s found' % type(arg))
    
    ##@brief Return a translation given a lang
    # @param lang str | None : If None return default lang translation
    def get(self, lang = None):
        lang = self.__default_lang if lang is None else lang
        if not self.lang_is_valid(lang):
            raise ValueError("Invalid lang : '%s'" % lang)
        elif lang in self.values:
            return self.values[lang]
        else:
            return str(self)

    ##@brief Set a translation
    # @param lang str : the lang
    # @param val str | None:  the translation if None delete the translation
    def set(self, lang, val):
        if not self.lang_is_valid(lang):
            raise ValueError("Invalid lang : '%s'" % lang)
        if not isinstance(val, str) and val is not None:
            raise ValueError("Expected a <class str> as value but got %s" % type(val))
        if val is None:
            del(self.values[lang])
        else:
            self.values[lang] = val

    ##@brief Checks that given lang is valid
    # @param cls MlString
    # @param lang str : the lang
    @classmethod
    def lang_is_valid(cls, lang):
        if not isinstance(lang, str):
            raise ValueError('Invalid value for lang. Str expected but %s found' % type(lang))
        return lang in cls.langs

    ##@brief Get or set the default lang
    @classmethod
    def default_lang(cls, lang = None):
        if lang is None:
            return cls.__default_lang
        if not cls.lang_is_valid(lang):
            raise ValueError('lang "%s" is not valid"' % lang)
        cls.__default_lang = lang
    
    ##@brief Return a mlstring loaded from a json string
    # @param cls MlString
    # @param json_str str : Json string
    @classmethod
    def from_json(cls, json_str):
        return MlString(json.loads(json_str))

    def __hash__(self):
        res = ''
        for lang in sorted(list(self.values.keys())):
            res = hash((res, lang, self.values[lang]))
        return res

    def d_hash(self):
        m = hashlib.md5()
        for lang in sorted(list(self.values.keys())):
            m.update(bytes(lang+";"+self.values[lang], 'utf-8'))
        return int.from_bytes(m.digest(), byteorder='big')

    def __eq__(self, a):
        return hash(self) == hash(a)
    
    ## @return The default langage translation or any available translation
    def __str__(self):
        if self.__default_lang in self.values:
            return self.values[self.__default_lang]
        else:
            return self.values[list(self.values.keys())[0]]

    def __repr__(self):
        return repr(self.values)
