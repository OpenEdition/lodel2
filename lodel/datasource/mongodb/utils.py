# -*- coding: utf-8 -*-

collection_prefix = {
    'relation': 'rel_',
    'collection': 'class_'
}


## @brief Returns a collection name given a Emclass name
# @param class_name str : The class name
# @return str
def object_collection_name(class_name):
    return ("%s%s" % (collection_prefix['object'], class_name)).lower()
