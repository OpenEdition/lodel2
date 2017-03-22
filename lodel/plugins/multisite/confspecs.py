from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

#Define a minimal confspec used by multisite loader and by lodelsites
#instance
LODEL2_CONFSPECS = {
    'lodel2.lodelsites': {
        #'name': (None,
        #    Validator('string', none_is_valid = False)), #replaced by lodel2.name
        'lodelsites_emfile': (None,
            Validator('string', none_is_valid = False)), #Bad validator
        'lodelsites_emtranslator': ('picklefile',
            Validator('strip', none_is_valid = False)), #Bad validator
        'sites_emfile': (None,
            Validator('string', none_is_valid = False)), #Bad validator
        'sites_emtranslator': ('picklefile',
            Validator('string', none_is_valid = False)), #Bad validator
    },
}
