# -*- coding: utf-8 -*-

import bson
from bson.son import SON
from collections import OrderedDict
import pymongo
from pymongo.errors import BulkWriteError
import urllib

from .utils import mongodbconnect, object_collection_name, parse_query_filters, parse_query_order, MONGODB_SORT_OPERATORS_MAP

class MongoDbDataSourceError(Exception):
    pass


class MongoDbDatasource(object):

    ## @brief instanciates a database object given a connection name
    # @param connection_name str
    def __init__(self, connection_name):
        self.database = mongodbconnect(connection_name)

    ## @brief returns a selection of documents from the datasource
    # @param target Emclass
    # @param field_list list
    # @param filters list : List of filters
    # @param rel_filters list : List of relational filters
    # @param order list : List of column to order. ex: order = [('title', 'ASC'),]
    # @param group list : List of tupple representing the column used as "group by" fields. ex: group = [('title', 'ASC'),]
    # @param limit int : Number of records to be returned
    # @param offset int: used with limit to choose the start record
    # @param instanciate bool : If true, the records are returned as instances, else they are returned as dict
    # @return list
    # @todo Implement the relations
    def select(self, target, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0, instanciate=True):
        collection_name = object_collection_name(target)
        collection = self.database[collection_name]
        query_filters = parse_query_filters(filters)
        query_result_ordering = parse_query_order(order) if order is not None else None
        results_field_list = None if len(field_list) == 0 else field_list
        limit = limit if limit is not None else 0

        if group is None:
            cursor = collection.find(filter=query_filters, projection=results_field_list, skip=offset, limit=limit, sort=query_result_ordering)
        else:
            pipeline = list()
            unwinding_list = list()
            grouping_dict = OrderedDict()
            sorting_list = list()
            for group_param in group:
                field_name = group_param[0]
                field_sort_option = group_param[1]
                sort_option = MONGODB_SORT_OPERATORS_MAP[field_sort_option]
                unwinding_list.append({'$unwind': '$%s' % field_name})
                grouping_dict[field_name] = '$%s' % field_name
                sorting_list.append((field_name, sort_option))

            sorting_list.extends(query_result_ordering)

            pipeline.append({'$match': query_filters})
            if results_field_list is not None:
                pipeline.append({'$project': SON([{field_name: 1} for field_name in field_list])})
            pipeline.extend(unwinding_list)
            pipeline.append({'$group': grouping_dict})
            pipeline.extend({'$sort': SON(sorting_list)})
            if offset > 0:
                pipeline.append({'$skip': offset})
            if limit is not None:
                pipeline.append({'$limit': limit})

        results = list()
        for document in cursor:
            results.append(document)

        return results

    ## @brief Deletes one record defined by its uid
    # @param target Emclass : class of the record to delete
    # @param uid dict|list : a dictionary of fields and values composing the unique identifier of the record or a list of several dictionaries
    # @return int : number of deleted records
    # @TODO Implement the error management
    def delete(self, target, uid):
        if isinstance(uid, dict):
            uid = [uid]
        collection_name = object_collection_name(target)
        collection = self.database[collection_name]
        result = collection.delete_many(uid)
        return result.deleted_count

    ## @brief updates one or a list of records
    # @param target Emclass : class of the object to insert
    # @param uids list : list of uids to update
    # @param datas dict : datas to update (new values)
    # @return int : Number of updated records
    # @todo check if the values need to be parsed
    def update(self, target, uids, **datas):
        if not isinstance(uids, list):
            uids = [uids]
        collection_name = object_collection_name(target)
        collection = self.database[collection_name]
        results = collection.update_many({'uid': {'$in': uids}}, datas)
        return results.modified_count()

    ## @brief Inserts a record in a given collection
    # @param target Emclass : class of the object to insert
    # @param datas dict : datas to insert
    # @return bool
    # @TODO Implement the error management
    def insert(self, target, **datas):
        collection_name = object_collection_name(target)
        collection = self.database[collection_name]
        result = collection.insert_one(datas)
        return len(result.inserted_id)

    ## @brief Inserts a list of records in a given collection
    # @param target Emclass : class of the objects inserted
    # @param datas_list
    # @return list : list of the inserted records' ids
    # @TODO Implement the error management
    def insert_multi(self, target, datas_list):
        collection_name = object_collection_name(target)
        collection = self.database[collection_name]
        result = collection.insert_many(datas_list)
        return len(result.inserted_ids)
