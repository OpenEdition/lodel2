from lodel.settings.validator import SettingValidator

__loader__ = 'main.py'

CONFSPEC = {
                'lodel2.datasources.*': {
                        'identifier': ( None,
                                        SettingValidator('string'))}}
