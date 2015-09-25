#-*- coding: utf-8 -*-

## @file editorialmodel.py
# Manage instance of an editorial model

import random
import time

import EditorialModel
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler
from EditorialModel.backend.dummy_backend import EmBackendDummy
from EditorialModel.classes import EmClass
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.types import EmType
from EditorialModel.classtypes import EmClassType
from Lodel.utils.mlstring import MlString
from EditorialModel.exceptions import EmComponentCheckError, EmComponentNotExistError, MigrationHandlerChangeError
import hashlib


## Manages the Editorial Model
class Model(object):

    components_class = [EmClass, EmType, EmFieldGroup, EmField]

    ## Constructor
    #
    # @param backend unknown: A backend object instanciated from one of the classes in the backend module
    def __init__(self, backend, migration_handler=None):
        if migration_handler is None:
            self.migration_handler = DummyMigrationHandler()
        elif issubclass(migration_handler.__class__, DummyMigrationHandler):
            self.migration_handler = migration_handler
        else:
            raise TypeError("migration_handler should be an instance from a subclass of DummyMigrationhandler")
        self.backend = None
        self.set_backend(backend)

        self._components = {'uids': {}, 'EmClass': [], 'EmType': [], 'EmField': [], 'EmFieldGroup': []}
        self.load()

    def __hash__(self):
        components_dump = ""
        for _, comp in self._components['uids'].items():
            components_dump += str(hash(comp))
        hashstring = hashlib.new('sha512')
        hashstring.update(components_dump.encode('utf-8'))
        return int(hashstring.hexdigest(), 16)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    @staticmethod
    ## Given a name return an EmComponent child class
    # @param class_name str : The name to identify an EmComponent class
    # @return A python class or False if the class_name is not a name of an EmComponent child class
    def emclass_from_name(class_name):
        for cls in Model.components_class:
            if cls.__name__ == class_name:
                return cls
        return False

    @staticmethod
    ## Given a python class return a name
    # @param cls : The python class we want the name
    # @return A class name as string or False if cls is not an EmComponent child class
    # @todo réécrire le split, c'est pas bô
    def name_from_emclass(em_class):
        if em_class not in Model.components_class:
            if issubclass(em_class, EmField):
                return 'EmField'
            return False
        return em_class.__name__

    ## Loads the structure of the Editorial Model
    #
    # Gets all the objects contained in that structure and creates a dict indexed by their uids
    # @todo Change the thrown exception when a components check fails
    # @throw ValueError When a component class don't exists
    def load(self):
        datas = self.backend.load()
        for uid, kwargs in datas.items():
            #Store and delete the EmComponent class name from datas
            cls_name = kwargs['component']
            del kwargs['component']

            if cls_name == 'EmField':
                #Special EmField process because of fieldtypes
                if not 'fieldtype' in kwargs:
                    raise AttributeError("Missing 'fieldtype' from EmField instanciation")
                cls = EditorialModel.fields.EmField.get_field_class(kwargs['fieldtype'])
            else:
                cls = self.emclass_from_name(cls_name)

            if cls:
                kwargs['uid'] = uid
                # create a dict for the component and one indexed by uids, store instanciated component in it
                self._components['uids'][uid] = cls(model=self, **kwargs)
                self._components[cls_name].append(self._components['uids'][uid])
            else:
                raise ValueError("Unknow EmComponent class : '" + cls_name + "'")

        #Sorting by rank
        for component_class in Model.components_class:
            self.sort_components(component_class)

        #Check integrity
        for uid, component in self._components['uids'].items():
            try:
                component.check()
            except EmComponentCheckError as exception_object:
                raise EmComponentCheckError("The component with uid %d is not valid. Check returns the following error : \"%s\"" % (uid, str(exception_object)))
            #Everything is done. Indicating that the component initialisation is over
            component.init_ended()

    ## Saves data using the current backend
    # @param filename str | None : if None use the current backend file (provided at backend instanciation)
    def save(self, filename = None):
        return self.backend.save(self, filename)

    ## Given a EmComponent child class return a list of instances
    # @param cls EmComponent : A python class
    # @return a list of instances or False if the class is not an EmComponent child
    def components(self, cls=None):
        if cls is None:
            return [ self.component(uid) for uid in self._components['uids'] ]
        key_name = self.name_from_emclass(cls)
        return False if key_name is False else self._components[key_name]

    ## Return an EmComponent given an uid
    # @param uid int : An EmComponent uid
    # @return The corresponding instance or False if uid don't exists
    def component(self, uid):
        return False if uid not in self._components['uids'] else self._components['uids'][uid]

    ## Sort components by rank in Model::_components
    # @param emclass pythonClass : The type of components to sort
    # @throw AttributeError if emclass is not valid
    # @warning disabled the test on component_class because of EmField new way of working
    def sort_components(self, component_class):
        #if component_class not in self.components_class:
        #    raise AttributeError("Bad argument emclass : '" + str(component_class) + "', excpeting one of " + str(self.components_class))

        self._components[self.name_from_emclass(component_class)] = sorted(self.components(component_class), key=lambda comp: comp.rank)

    ## Return a new uid
    # @return a new uid
    def new_uid(self):
        used_uid = [int(uid) for uid in self._components['uids'].keys()]
        return sorted(used_uid)[-1] + 1 if len(used_uid) > 0 else 1

    ## Create a component from a component type and datas
    #
    # @note if datas does not contains a rank the new component will be added last
    # @note datas['rank'] can be an integer or two specials strings 'last' or 'first'
    # @param component_type str : a component type ( component_class, component_fieldgroup, component_field or component_type )
    # @param datas dict : the options needed by the component creation
    # @throw ValueError if datas['rank'] is not valid (too big or too small, not an integer nor 'last' or 'first' )
    # @todo Handle a raise from the migration handler
    # @todo Transform the datas arg in **datas ?
    def create_component(self, component_type, datas, uid=None):
        if not (uid is None) and (not isinstance(uid, int) or uid <= 0 or uid in self._components['uids']):
            raise ValueError("Invalid uid provided")
        
        if component_type not in [ n for n in self._components.keys() if n != 'uids' ]:
            raise ValueError("Invalid component_type rpovided")
        elif component_type == 'EmField':
            #special process for EmField
            if not 'fieldtype' in datas:
                raise AttributeError("Missing 'fieldtype' from EmField instanciation")
            em_obj = EditorialModel.fields.EmField.get_field_class(datas['fieldtype'])
        else:
            em_obj = self.emclass_from_name(component_type)

        rank = 'last'
        if 'rank' in datas:
            rank = datas['rank']
            del datas['rank']

        datas['uid'] = uid if uid else self.new_uid()
        em_component = em_obj(model=self, **datas)

        em_component.rank = em_component.get_max_rank() + 1 #  Inserting last by default

        self._components['uids'][em_component.uid] = em_component
        self._components[component_type].append(em_component)

        if rank != 'last':
            em_component.set_rank(1 if rank == 'first' else rank)

        #everything done, indicating that initialisation is over
        em_component.init_ended()

        #register the creation in migration handler
        try:
            self.migration_handler.register_change(self, em_component.uid, None, em_component.attr_dump())
        except MigrationHandlerChangeError as exception_object:
            #Revert the creation
            self.components(em_component.__class__).remove(em_component)
            del self._components['uids'][em_component.uid]
            raise exception_object

        self.migration_handler.register_model_state(self, hash(self))

        return em_component

    ## Delete a component
    # @param uid int : Component identifier
    # @throw EmComponentNotExistError
    # @todo unable uid check
    # @todo Handle a raise from the migration handler
    def delete_component(self, uid):
        em_component = self.component(uid)
        if not em_component:
            raise EmComponentNotExistError()

        if em_component.delete_check():
            #register the deletion in migration handler
            self.migration_handler.register_change(self, uid, self.component(uid).attr_dump(), None)

            # delete internal lists
            self._components[self.name_from_emclass(em_component.__class__)].remove(em_component)
            del self._components['uids'][uid]

            #Register the new EM state
            self.migration_handler.register_model_state(self, hash(self))
            return True

        return False

    ## Changes the current backend
    #
    # @param backend unknown: A backend object
    def set_backend(self, backend):
        if issubclass(backend.__class__, EmBackendDummy):
            self.backend = backend
        else:
            raise TypeError('Backend should be an instance of a EmBackednDummy subclass')

    ## Returns a list of all the EmClass objects of the model
    def classes(self):
        return list(self._components[self.name_from_emclass(EmClass)])

    ## Use a new migration handler, re-apply all the ME to this handler
    #
    # @param new_mh MigrationHandler: A migration_handler object
    # @warning : if a relational-attribute field (with 'rel_field_id') comes before it's relational field (with 'rel_to_type_id'), this will blow up
    def migrate_handler(self, new_mh):
        new_me = Model(EmBackendDummy(), new_mh)
        relations = {'fields_list': [], 'superiors_list': []}

        # re-create component one by one, in components_class[] order
        for cls in self.components_class:
            for component in self.components(cls):
                component_type = self.name_from_emclass(cls)
                component_dump = component.attr_dump()
                # Save relations between component to apply them later
                for relation in relations.keys():
                    if relation in component_dump and component_dump[relation]:
                        relations[relation].append((component.uid, component_dump[relation]))
                        del component_dump[relation]
                new_me.create_component(component_type, component_dump, component.uid)

        # apply selected field  to types
        for fields_list in relations['fields_list']:
            uid, fields = fields_list
            for field_id in fields:
                new_me.component(uid).select_field(new_me.component(field_id))

        # add superiors to types
        for superiors_list in relations['superiors_list']:
            uid, sup_list = superiors_list
            for nature, superiors_uid in sup_list.items():
                for superior_uid in superiors_uid:
                    new_me.component(uid).add_superior(new_me.component(superior_uid), nature)

        del new_me

        self.migration_handler = new_mh

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
    # @return A randomly generate EM
    def random(cls, backend, **kwargs):
        em = Model(backend)

        chances = {
            'classtype' : 0, # a class in classtype
            'nclass': 5, #max number of classes per classtype
            'nofg': 10, #no fieldgroup in a class
            'nfg': 5, #max number of fieldgroups per classes
            'notype': 10, # no types in a class
            'ntype': 8,  # max number of types in a class
            'seltype': 2, #chances to select an optional field
            'ntypesuperiors': 2, #chances to link with a superior
            'nofields': 10, # no fields in a fieldgroup
            'nfields' : 8, #max number of fields per fieldgroups
            'rfields': 5,#max number of attributes relation fields
            'optfield': 2, #chances to be optionnal
        }

        for name,value in kwargs.items():
            if name not in chances:
                #warning
                pass
            else:
                chances[name] = value

        #classes creation
        for classtype in EmClassType.getall():
            if random.randint(0,chances['classtype']) == 0:
                for _ in range(random.randint(1,chances['nclass'])):
                    cdats = cls._rnd_component_datas()
                    cdats['classtype'] = classtype['name']
                    em.create_component('EmClass', cdats)

        for emclass in em.classes():
            #fieldgroups creation
            if random.randint(0, chances['nofg']) != 0:
                for _ in range(random.randint(1, chances['nfg'])):
                    fgdats = cls._rnd_component_datas()
                    fgdats['class_id'] = emclass.uid
                    em.create_component('EmFieldGroup', fgdats)

            #types creation
            if random.randint(0, chances['notype']) != 0:
                for _ in range(random.randint(1, chances['ntype'])):
                    tdats = cls._rnd_component_datas()
                    tdats['class_id'] = emclass.uid
                    em.create_component('EmType', tdats)

        #random type hierarchy
        for emtype in em.components(EmType):
            possible = emtype.possible_superiors()
            for nat in possible:
                if len(possible[nat]) > 0 and random.randint(0, chances['ntypesuperiors']) == 0:
                    random.shuffle(possible[nat])
                    for i in range(random.randint(1, len(possible[nat]))):
                        emtype.add_superior(possible[nat][i], nat)


        #fields creation
        ft_l = EmField.fieldtypes_list()
        for emfg in em.components(EmFieldGroup):
            if random.randint(0, chances['nofields']) != 0:
                for _ in range(random.randint(1, chances['nfields'])):
                    ft = ft_l[random.randint(0,len(ft_l)-1)]
                    fdats = cls._rnd_component_datas()
                    fdats['fieldtype']=ft
                    fdats['fieldgroup_id'] = emfg.uid
                    if ft == 'rel2type':
                        emtypes = em.components(EmType)
                        fdats['rel_to_type_id'] = emtypes[random.randint(0,len(emtypes)-1)].uid
                    if random.randint(0,chances['optfield']) == 0:
                        fdats['optional'] = True
                    em.create_component('EmField', fdats)

        #relationnal fiels creation
        ft_l = [ ft for ft in EmField.fieldtypes_list() if ft != 'rel2type' ]
        for emrelf in [ f for f in em.components(EmField) if f.ftype == 'rel2type' ]:
            for _ in range(0,chances['rfields']):
                ft = ft_l[random.randint(0, len(ft_l)-1)]
                fdats = cls._rnd_component_datas()
                fdats['fieldtype'] = ft
                fdats['fieldgroup_id'] = emrelf.fieldgroup_id
                if random.randint(0, chances['optfield']) == 0:
                    fdats['optional'] = True
                em.create_component('EmField', fdats)
                

        #selection optionnal fields
        for emtype in em.components(EmType):
            selectable = [field for fieldgroup in emtype.fieldgroups() for field in fieldgroup.fields() if field.optional ]
            for field in selectable:
                if random.randint(0,chances['seltype']) == 0:
                    emtype.select_field(field)
                    

        return em

                
    
    @staticmethod
    ## @brief Generate a random string
    # @warning dirty cache trick with globals()
    # @return a randomly selected string
    def _rnd_str(words_src='/usr/share/dict/words'):
        if '_words' not in globals() or globals()['_words_fname'] != words_src:
            globals()['_words_fname'] = words_src
            with open(words_src, 'r') as fpw:
                globals()['_words'] = [ l.strip() for l in fpw ]
        words = globals()['_words']
        return words[random.randint(0,len(words)-1)]
        
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
        mlstr_nlang = 2;
        ret = dict()
        ret['name'] = cls._rnd_str()
        ret['string'] = cls._rnd_mlstr(mlstr_nlang)
        ret['help_text'] = cls._rnd_mlstr(mlstr_nlang)

        return ret
        
        
        
