#-*- coding: utf-8 -*-

from lodel.settings.validator import SettingValidator

CONFSPEC = {
                'lodel2.datasources.*': {
                        'identifier': ( None,
                                        SettingValidator('string'))}}
