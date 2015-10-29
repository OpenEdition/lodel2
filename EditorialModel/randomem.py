#-*- coding: utf-8 -*-

## @package EditorialModel.randomem
#
# Provide methods for random EM generation

import random
from EditorialModel.backend.dummy_backend import EmBackendDummy
from EditorialModel.model import Model
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.types import EmType
from EditorialModel.classtypes import EmClassType
from Lodel.utils.mlstring import MlString


class RandomEm(object):
    
    ## @brief Instanciate a class allowing to generate random EM
    # @see RandomEm::random_em()
    def __init__(self, backend=None, **kwargs):
        self.backend = backend
        self.kwargs = kwargs

    ## @brief Return a random EM
    # @return A random EM
    def gen(self):
        return self.random_em(self.backend, **self.kwargs)

    @classmethod
    ## @brief Generate a random editorial model
    #
    # The random generator can be tuned with integer parameters
    # that represent probability or maximum numbers of items.
    # The probability (chances) works like 1/x chances to append
    # with x the tunable parameter
    # Tunable generator parameters :
    # - classtype : Chances for a classtype to be empty (default 0)
    # - nclass : Maximum number of classes per classtypes (default 5)
    # - nofg : Chances for a classe to have no fieldgroup associated to it (default 10)
    # - notype : Chances for a classe to have no type associated to it (default 5)
    # - seltype : Chances for a type to select an optionnal field (default 2)
    # - ntypesuperiors : Chances for a type to link with a superiors (default 3)
    # - nofields : Chances for a fieldgroup to be empty (default 10)
    # - nfields : Maximum number of field per fieldgroups (default 8)
    # - rfields : Maximum number of relation_to_type attributes fields (default 5)
    # - optfield : Chances for a field to be optionnal (default 2)
    # @param backend : A backend to use with the new EM
    # @param **kwargs dict : Provide tunable generation parameter
    # @param cls
    # @return A randomly generate EM
    def random_em(cls, backend=None, **kwargs):
        ed_mod = Model(EmBackendDummy if backend is None else backend)

        chances = {
            'classtype': 0,         # a class in classtype
            'nclass': 5,            # max number of classes per classtype
            'nofg': 10,             # no fieldgroup in a class
            'nfg': 5,               # max number of fieldgroups per classes
            'notype': 10,           # no types in a class
            'ntype': 8,             # max number of types in a class
            'seltype': 2,           # chances to select an optional field
            'ntypesuperiors': 2,    # chances to link with a superior
            'nofields': 10,         # no fields in a fieldgroup
            'nfields': 8,           # max number of fields per fieldgroups
            'nr2tfields': 1,        # max number of rel2type fields per fieldgroups
            'rfields': 5,           # max number of attributes relation fields
            'optfield': 2,          # chances to be optionnal
        }

        for name, value in kwargs.items():
            if name not in chances:
                #warning
                pass
            else:
                chances[name] = value

        #classes creation
        for classtype in EmClassType.getall():
            if random.randint(0, chances['classtype']) == 0:
                for _ in range(random.randint(1, chances['nclass'])):
                    cdats = cls._rnd_component_datas()
                    cdats['classtype'] = classtype['name']
                    ed_mod.create_component('EmClass', cdats)

        for emclass in ed_mod.classes():
            #fieldgroups creation
            if random.randint(0, chances['nofg']) != 0:
                for _ in range(random.randint(1, chances['nfg'])):
                    fgdats = cls._rnd_component_datas()
                    fgdats['class_id'] = emclass.uid
                    ed_mod.create_component('EmFieldGroup', fgdats)

            #types creation
            if random.randint(0, chances['notype']) != 0:
                for _ in range(random.randint(1, chances['ntype'])):
                    tdats = cls._rnd_component_datas()
                    tdats['class_id'] = emclass.uid
                    ed_mod.create_component('EmType', tdats)

        #random type hierarchy
        for emtype in ed_mod.components(EmType):
            possible = emtype.possible_superiors()
            for nat in possible:
                if len(possible[nat]) > 0 and random.randint(0, chances['ntypesuperiors']) == 0:
                    random.shuffle(possible[nat])
                    for i in range(random.randint(1, len(possible[nat]))):
                        emtype.add_superior(possible[nat][i], nat)

        #fields creation
        ft_l = [ ftname for ftname in EmField.fieldtypes_list() if ftname != 'pk' and ftname != 'rel2type']
        for emfg in ed_mod.components(EmFieldGroup):
            if random.randint(0, chances['nofields']) != 0:
                for _ in range(random.randint(1, chances['nfields'])):
                    field_type = ft_l[random.randint(0, len(ft_l) - 1)]
                    fdats = cls._rnd_component_datas()
                    fdats['fieldtype'] = field_type
                    fdats['fieldgroup_id'] = emfg.uid
                    if random.randint(0, chances['optfield']) == 0:
                        fdats['optional'] = True
                    ed_mod.create_component('EmField', fdats)
        
        #rel2type creation (in case none where created before
        for emfg in ed_mod.components(EmFieldGroup):    
            for _ in range(random.randint(0, chances['nr2tfields'])):
                field_type = 'rel2type'
                fdats = cls._rnd_component_datas()
                fdats['fieldtype'] = field_type
                fdats['fieldgroup_id'] = emfg.uid
                emtypes = ed_mod.components(EmType)
                fdats['rel_to_type_id'] = emtypes[random.randint(0, len(emtypes) - 1)].uid
                if random.randint(0, chances['optfield']) == 0:
                    fdats['optional'] = True
                ed_mod.create_component('EmField', fdats)


        #relationnal fields creation
        ft_l = [field_type for field_type in EmField.fieldtypes_list() if field_type != 'rel2type' and field_type  != 'pk']
        for emrelf in [f for f in ed_mod.components(EmField) if f.fieldtype == 'rel2type']:
            for _ in range(0, chances['rfields']):
                field_type = ft_l[random.randint(0, len(ft_l) - 1)]
                fdats = cls._rnd_component_datas()
                fdats['rel_field_id'] = emrelf.uid
                fdats['fieldtype'] = field_type
                fdats['fieldgroup_id'] = emrelf.fieldgroup_id
                if random.randint(0, chances['optfield']) == 0:
                    fdats['optional'] = True
                ed_mod.create_component('EmField', fdats)

        #selection optionnal fields
        for emtype in ed_mod.components(EmType):
            selectable = [field for fieldgroup in emtype.fieldgroups() for field in fieldgroup.fields() if field.optional]
            for field in selectable:
                if random.randint(0, chances['seltype']) == 0:
                    emtype.select_field(field)
        return ed_mod

    @staticmethod
    ## @brief Generate a random string
    # @warning dirty cache trick with globals()
    # @return a randomly selected string
    def _rnd_str(words_src='/usr/share/dict/words'):
        if '_words' not in globals() or globals()['_words_fname'] != words_src:
            globals()['_words_fname'] = words_src
            with open(words_src, 'r') as fpw:
                globals()['_words'] = [l.strip() for l in fpw]
        words = globals()['_words']
        return words[random.randint(0, len(words) - 1)]

    @classmethod
    ## @brief Generate a random MlString
    # @param nlng : Number of langs in the MlString
    # @return a random MlString with nlng translations
    # @todo use a dict to generated langages
    def _rnd_mlstr(cls, nlng):
        ret = MlString()
        for _ in range(nlng):
            ret.set(cls._rnd_str(), cls._rnd_str())
        return ret

    @classmethod
    ## @brief returns randomly generated datas for an EmComponent
    # @return a dict with name, string and help_text
    def _rnd_component_datas(cls):
        mlstr_nlang = 2
        ret = dict()
        ret['name'] = cls._rnd_str()
        ret['string'] = cls._rnd_mlstr(mlstr_nlang)
        ret['help_text'] = cls._rnd_mlstr(mlstr_nlang)

        return ret
