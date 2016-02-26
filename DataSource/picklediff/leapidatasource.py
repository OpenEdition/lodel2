#-*- coding: utf-8 -*-

import os, os.path
import pickle
import re
import copy
from collections import OrderedDict

from Lodel.settings import Settings
from Lodel import logger

from EditorialModel.fieldtypes import pk

## @brief Datasource designed to stores datas and datas diff in pickle files
# 
# @note designed to handle editorial model storage
#
# Datas organisation :
#
# - editorial_model :
#  - components : dict with lodel_id as key and datas dict as value
#   - datas : dict with field name as key and field value as value
#  - class_link : dict with leo class as key and sets of lodel_id as value
# - states : dict with editorial_model state hash as key and modifications_datas dict as value
#  - modifications_datas : dict with action key and arguements for actions (example : { 'action': 'insert', 'target_class': EmClass, 'datas': dict() }
#
class LeapiDataSource(object):
 
    autohandled_fieldtypes = [
        {'ftype': pk.EmFieldType}
    ]

    def __init__(self, filename = None):
        if filename is None:
            filename = Settings.datasource_options['filename']
        self.__filename = filename
        self.__content = None
        self.__load_file()
        
    def select(self, target_cls, field_list, filters, rel_filters = None, order = None, group = None, limit = None, offset = 0, instanciate = True):
        if not target_cls.is_leobject() and target_cls.__class__ != target_cls.name2class('Lerelation'):
            if target_cls.__name__ not in self.__content['editorial_model']['class_link'] or len(self.__content['editorial_model']['class_link'][target_cls.__name__]) == 0:
                return []
            lodel_ids = list(self.__content['editorial_model']['class_link'][target_cls.__name__])
        else:
            lodel_ids = list(self.__content['editorial_model']['components'].keys())
            
        for field, cmp_op, value in filters:
            if cmp_op.endswith('like '): # *like case
                value.replace('%', '.*')
                tmp_ids = []
                for lodel_id in lodel_ids:
                    match = re.match(value, self.__field_value(lodel_id, field))
                    if (cmp_op == ' like ' and match) or (cmp_op == ' not like ' and not match):
                        tmp_ids.append(lodel_ids)
                    elif cmp_op == ' in ':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) in value]
                    elif cmp_op == ' not in ':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) not in value]
                    elif cmp_op == '=':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) == value]
                    elif cmp_op == '<=':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) <= value]
                    elif cmp_op == '>=':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) <= value]
                    elif cmp_op == '!=':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) != value]
                    elif cmp_op == '<':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) < value]
                    elif cmp_op == '>':
                        lodel_ids = [ lid for lid in lodel_ids if self.__field_value(lodel_id, field) < value]
        # Now we got filtered lodel_id list in lodel_ids
        result = []
        for datas in [ copy.copy(self.__content['editorial_model']['components'][lodel_id]) for lodel_id in lodel_ids ]:
            comp_class = target_cls.name2class(datas['__component_leapi_class__'])
            del(datas['__component_leapi_class__'])

            if instanciate:
                # Don't care about field_list... maybe it's not a good idea ?
                result.append(comp_class(**datas))
            else:
                result.append({ fname: datas[fname] for fname in field_list })
        return result
            

    def delete(self, target_cls, leo_id):
        if leo_id not in self.__content['editorial_model']['class_link'][target_cls.__name__]:
            raise AttributeError("No %s with id %d" % (target_cls.__name__, leo_id))
        self.__content['editorial_model']['class_link'][target_cls.__name__] -= set([leo_id])
        self.__content['editorial_model']['class_link'][target_cls.leclass.__name__] -= set([leo_id])
        del(self.__content['editorial_model']['components'][leo_id])
        self.__register_modification('delete', {'target_cls': target_cls, 'leo_id': leo_id})

    def update(self, target_cls, leo_id, **datas):
        if leo_id not in self.__content['editorial_model']['class_link'][target_cls.__name__]:
            raise AttributeError("No %s with id %d" % (target_cls.__name__, leo_id))
        for key, value in datas.items():
            self.__content['editorial_model']['components'][leo_id][key] = value #no checks, leapi should have checked before...
        self.__register_modification('update', {'target_cls': target_cls, 'leo_id': leo_id, 'datas': datas})
        pass

    def insert(self, target_cls, **datas):
        new_id = self.__new_id()
        datas[self.__id_name(target_cls)] = new_id
        # Adding target_cls to datas
        datas['__component_leapi_class__'] = target_cls.__name__
        # Adding the component to component list
        self.__content['editorial_model']['components'][new_id] = datas
        # Creating class_link type entry
        if target_cls.__name__ not in self.__content['editorial_model']['class_link']:
            self.__content['editorial_model']['class_link'][target_cls.__name__] = set()
        self.__content['editorial_model']['class_link'][target_cls.__name__] |= set([new_id])
        # Creating class_link class entry
        if target_cls._leclass.__name__ not in self.__content['editorial_model']['class_link']:
            self.__content['editorial_model']['class_link'][target_cls._leclass.__name__] = set()
        self.__content['editorial_model']['class_link'][target_cls._leclass.__name__] |= set([new_id])

        self.__register_modification('insert', {'target_cls': target_cls, 'datas': datas})
        return new_id

    def insert_multi(self, target_cls, datas_list):
        pass

    def update_rank(self, le_relation, new_rank):
        pass

    def __id_name(self, target_cls):
        return 'lodel_id' if target_cls.implements_leobject() else 'relation_id'

    def __new_id(self):
        # Find a new component id avoiding 'id holes'
        lodel_id = 1
        while lodel_id in self.__content['editorial_model']['components'].keys():
            lodel_id += 1
        return lodel_id

    ## @brief Save memory repr of em into pickle file
    def __save(self):
        with open(self.__filename, 'wb') as ffd:
            pickle.dump(self.__content, ffd)
    
    ## @brief Loads self.__content from self.__filename
    def __load_file(self):
        if not os.path.isfile(self.__filename):
            logger.debug("File %s not found !" % self.__filename)
            self.__content = dict()
        else:
            with open(self.__filename, 'rb') as ffd:
                self.__content = pickle.load(ffd)
        # dict initialisation
        if self.__content is None:
            self.__content = dict()
        else:
            logger.debug("Loaded : \n %s" % self.__content)
        if 'editorial_model' not in self.__content:
            self.__content['editorial_model'] = OrderedDict()
        if 'components' not in self.__content['editorial_model']:
            self.__content['editorial_model']['components'] = OrderedDict()
        if 'class_link' not in self.__content['editorial_model']:
            self.__content['editorial_model']['class_link'] = OrderedDict()
        if 'states' not in self.__content:
            self.__content['states'] = OrderedDict()

    ## @brief Method that register a EM modification
    # @warning this method MUST be called once the modification is made in the __content dict
    # 
    # @param action str : name of modification (update, delete or insert)
    # @param kwargs dict : action arguments
    def __register_modification(self, action, kwargs):
        logger.debug("Registered a modification : action = %s kwargs = %s" % (action, kwargs))
        em_hash = hash(pickle.dumps(self.__content['editorial_model']))
        self.__content['states'][em_hash] = (action, kwargs)
        self.__save()

    ## @brief Given a lodel_id and a field name return the field value
    # @return the field value of designated LeObject
    def __field_value(self, lodel_id, field_name):
        return self.__content['editorial_model']['components'][lodel_id][field_name]
