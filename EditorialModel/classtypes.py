# -*- coding: utf-8 -*-

"""
    representation of the classTypes (sic…)
"""

class EmNature(object):
    PARENT = 'parent'
    TRANSLATION = 'translation'
    IDENTITY = 'identity'

class EmClassType(object):

    entity = {
        'name' : 'entity',
        'hierarchy' : [
            {
                'nature'   : EmNature.PARENT,
                'attach'   : 'type',
                'editable' : True,
            },
            {
                'nature'   : EmNature.TRANSLATION,
                'attach'   : 'type',
                'editable' : True,
            },
        ],
    }

    entry = {
        'name' : 'entry',
        'hierarchy' : [
            {
                'nature'   : EmNature.PARENT,
                'attach'   : 'type',
                'editable' : True,
            },
            {
                'nature'   : EmNature.TRANSLATION,
                'attach'   : 'type',
                'editable' : True,
            },
        ],
    }

    person = {
        'name' : 'person',
        'hierarchy' : [
            {
                'nature'   : EmNature.IDENTITY,
                'attach'   : 'classtype',
                'editable' : False,
            },
        ],
    }
