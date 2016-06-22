# -*- coding: utf-8 -*-

import re
import warnings
from bson.son import SON
from collections import OrderedDict
import pymongo
from pymongo.errors import BulkWriteError

from lodel import logger

from . import utils
from .utils import object_collection_name,\
    MONGODB_SORT_OPERATORS_MAP, connection_string

class MongoDbDataSourceError(Exception):
    pass

class MongoDbDatasource(object):

    ##@brief Stores existing connections
    #
    #The key of this dict is a hash of the connection string + ro parameter.
    #The value is a dict with 2 keys :
    # - conn_count : the number of instanciated datasource that use this
    #connection
    # - db : the pymongo database object instance
    _connections = dict()

    ##@brief Mapping from lodel2 operators to mongodb operator
    lodel2mongo_op_map = {
        '=':'$eq', '<=':'$lte', '>=':'$gte', '!=':'$ne', '<':'$lt',
        '>':'$gt', 'in':'$in', 'not in':'$nin' }
    ##@brief List of mongodb operators that expect re as value
    mongo_op_re = ['$in', '$nin']
    wildcard_re = re.compile('[^\\\\]\*')

    ##@brief instanciates a database object given a connection name
    #@param host str : hostname or IP
    #@param port int : mongodb listening port
    #@param db_name str
    #@param username str
    #@param password str
    #@param ro bool : If True the Datasource is for read only, else the
    #Datasource is write only !
    def __init__(self, host, port, db_name, username, password, read_only = False):
        ##@brief Connections infos that can be kept securly
        self.__db_infos = {'host': host, 'port': port, 'db_name': db_name}
        ##@brief Is the instance read only ? (if not it's write only)
        self.__read_only = bool(read_only)
        ##@brief Uniq ID for mongodb connection
        self.__conn_hash= None
        ##@brief Stores the database cursor
        self.database = self.__connect(
            username, password, ro = self.__read_only)

    ##@brief Destructor that attempt to close connection to DB
    #
    #Decrease the conn_count of associated MongoDbDatasource::_connections
    #item. If it reach 0 close the connection to the db
    #@see MongoDbDatasource::__connect()
    def __del__(self):
        self._connections[self.__conn_hash]['conn_count'] -= 1
        if self._connections[self.__conn_hash]['conn_count'] <= 0:
            self._connections[self.__conn_hash]['db'].close()
            del(self._connections[self.__conn_hash])
            logger.info("Closing connection to database")

    ##@brief Provide a new uniq numeric ID
    #@param emcomp LeObject subclass (not instance) : To know on wich things we
    #have to be uniq
    #@warning multiple UID broken by this method
    #@return an integer
    def new_numeric_id(self, emcomp):
        target = emcomp.uid_source()
        tuid = target._uid[0] # Multiple UID broken here
        results = self.select(
            target, [tuid], [], order=[(tuid, 'DESC')], limit = 1)
        return results[0][tuid]+1

    ##@brief returns a selection of documents from the datasource
    #@param target Emclass
    #@param field_list list
    #@param filters list : List of filters
    #@param rel_filters list : List of relational filters
    #@param order list : List of column to order. ex: order = [('title', 'ASC'),]
    #@param group list : List of tupple representing the column used as "group by" fields. ex: group = [('title', 'ASC'),]
    #@param limit int : Number of records to be returned
    #@param offset int: used with limit to choose the start record
    #@param instanciate bool : If true, the records are returned as instances, else they are returned as dict
    #@return list
    #@todo Implement the relations
    def select(self, target, field_list, filters = None, rel_filters=None, order=None, group=None, limit=None, offset=0):
        results = list()
        if target.abstract:
            target_childs = target.child_classes()
            for target_child in target_childs:
                results.append(self.select(target=target, field_list=field_list, filters=filters,
                                           rel_filters=rel_filters, order=order, group=group, limit=limit,
                                           offset=offset))
        else:
            # Default arg init
            filters = [] if filters is None else filters
            rel_filters = [] if rel_filters is None else rel_filters

            collection_name = object_collection_name(target)
            collection = self.database[collection_name]

            query_filters = self.__process_filters(target, filters, rel_filters)
            query_result_ordering = None
            if order is not None:
                query_result_ordering = utils.parse_query_order(order)
            results_field_list = None if len(field_list) == 0 else field_list
            limit = limit if limit is not None else 0

            if group is None:
                cursor = collection.find(
                    filter=query_filters, projection=results_field_list,
                    skip=offset, limit=limit, sort=query_result_ordering)
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
                    pipeline.append({
                        '$project': SON([{field_name: 1}
                        for field_name in field_list])})
                pipeline.extend(unwinding_list)
                pipeline.append({'$group': grouping_dict})
                pipeline.extend({'$sort': SON(sorting_list)})
                if offset > 0:
                    pipeline.append({'$skip': offset})
                if limit is not None:
                    pipeline.append({'$limit': limit})

            #results = list()
            for document in cursor:
                results.append(document)

        return results

    ##@brief Deletes records according to given filters
    #@param target Emclass : class of the record to delete
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@return int : number of deleted records
    def delete(self, target, filters, relational_filters):
        mongo_filters = self.__process_filters(
            target, filters, relational_filters)
        res = self.__collection(target).delete_many(mongo_filters)
        return res.deleted_count

    ## @brief updates records according to given filters
    #@param target Emclass : class of the object to insert
    #@param filters list : List of filters
    #@param rel_filters list : List of relational filters
    #@param upd_datas dict : datas to update (new values)
    #@return int : Number of updated records
    def update(self, target, filters, relational_filters, upd_datas):
        mongo_filters = self.__process_filters(
            target, filters, relational_filters)
        res = self.__collection(target).update_many(mongo_filters, upd_datas)
        return res.modified_count()

    ## @brief Inserts a record in a given collection
    # @param target Emclass : class of the object to insert
    # @param new_datas dict : datas to insert
    # @return the inserted uid
    def insert(self, target, new_datas):
        res = self.__collection(target).insert(new_datas)
        return str(res)

    ## @brief Inserts a list of records in a given collection
    # @param target Emclass : class of the objects inserted
    # @param datas_list list : list of dict
    # @return list : list of the inserted records' ids
    def insert_multi(self, target, datas_list):
        res = self.__collection(target).insert_many(datas_list)
        return list(res.inserted_ids)

    ##@brief Connect to database
    #@not this method avoid opening two times the same connection using
    #MongoDbDatasource::_connections static attribute
    #@param host str : hostname or IP
    #@param port int : mongodb listening port
    #@param db_name str
    #@param username str
    #@param password str
    #@param ro bool : If True the Datasource is for read only, else the
    def __connect(self, username, password, ro):
        conn_string = connection_string(
            username = username, password = password,
            host = self.__db_infos['host'],
            port = self.__db_infos['port'])

        conn_string += "__ReadOnly__:"+str(self.__read_only)
        self.__conn_hash = conn_h = hash(conn_string)
        if conn_h in self._connections:
            self._connections[conn_h]['conn_count'] += 1
            return self._connections[conn_h]['db'][self.__db_infos['db_name']]
        else:
            logger.info("Opening a new connection to database")
            self._connections[conn_h] = {
                'conn_count': 1,
                'db': utils.connection(
                    host = self.__db_infos['host'],
                    port = self.__db_infos['port'],
                    username = username, 
                    password = password)}
            return self._connections[conn_h]['db'][self.__db_infos['db_name']]
                    

    ##@brief Return a pymongo collection given a LeObject child class
    #@param leobject LeObject child class (no instance)
    #return a pymongo.collection instance
    def __collection(self, leobject):
        return self.database[object_collection_name(leobject)]

    ##@brief Perform subqueries implies by relational filters and append the
    # result to existing filters
    #
    #The processing is divided in multiple steps :
    # - determine (for each relational field of the target)  every collection
    #that are involved
    # - generate subqueries for relational_filters that concerns a different
    #collection than target collection
    #filters
    # - execute subqueries
    # - transform subqueries results in filters
    # - merge subqueries generated filters with existing filters
    #
    #@param target LeObject subclass (no instance) : Target class
    #@param filters list : List of tuple(FIELDNAME, OP, VALUE)
    #@param relational_filters : same composition thant filters except that
    # FIELD is represented by a tuple(FIELDNAME, {CLASS1:RFIELD1,
    # CLASS2:RFIELD2})
    #@return a list of pymongo filters ( dict {FIELD:{OPERATOR:VALUE}} )
    def __process_filters(self,target, filters, relational_filters):
        # Simple filters lodel2 -> pymongo converting
        res = self.__filters2mongo(filters)
        rfilters = self.__prepare_relational_filters(target, relational_filters)
        #Now that everything is well organized, begin to forge subquerie
        #filters
        self.__subqueries_from_relational_filters(target, rfilters)
        # Executing subqueries, creating filters from result, and injecting
        # them in original filters of the query
        if len(rfilters) > 0:
            logger.debug("Begining subquery execution")
        for fname in rfilters:
            if fname not in res:
                res[fname] = dict()
            subq_results = set()
            for leobject, sq_filters in rfilters[fname].items():
                uid_fname = mongo_fieldname(leobject._uid)
                log_msg = "Subquery running on collection {coll} with filters \
'{filters}'"
                logger.debug(log_msg.format(
                    coll=object_collection_name(leobject),
                    filters=sq_filters))

                cursor = self.__collection(leobject).find(
                    filter=sq_filters,
                    projection=uid_fname)
                subq_results |= set(doc[uid_fname] for doc in cursor)
            #generating new filter from result
            if '$in' in res[fname]:
                #WARNING we allready have a IN on this field, doing dedup
                #from result
                deduped = set(res[fname]['$in']) & subq
                if len(deduped) == 0:
                    del(res[fname]['$in'])
                else:
                    res[fname]['$in'] = list(deduped)
            else:
                res[fname]['$in'] = list(subq_results)
        if len(rfilters) > 0:
            logger.debug("End of subquery execution")
        return res

    ##@brief Generate subqueries from rfilters tree
    #
    #Returned struct organization :
    # - 1st level keys : relational field name of target
    # - 2nd level keys : referenced leobject
    # - 3th level values : pymongo filters (dict)
    #
    #@note The only caller of this method is __process_filters
    #@warning No return value, the rfilters arguement is modified by
    #reference
    #
    #@param target LeObject subclass (no instance) : Target class
    #@param rfilters dict : A struct as returned by
    #MongoDbDatasource.__prepare_relational_filters()
    #@return None, the rfilters argument is modified by reference
    @classmethod
    def __subqueries_from_relational_filters(cls, target, rfilters):
        for fname in rfilters:
            for leobject in rfilters[fname]:
                for rfield in rfilters[fname][leobject]:
                    #This way of doing is not optimized but allows to trigger
                    #warnings in some case (2 different values for a same op
                    #on a same field on a same collection)
                    mongofilters = cls.__op_value_listconv(
                        rfilters[fname][leobject][rfield])
                    rfilters[fname][leobject][rfield] = mongofilters

    ##@brief Generate a tree from relational_filters
    #
    #The generated struct is a dict with :
    # - 1st level keys : relational field name of target
    # - 2nd level keys : referenced leobject
    # - 3th level keys : referenced field in referenced class
    # - 4th level values : list of tuple(op, value)
    #
    #@note The only caller of this method is __process_filters
    #@warning An assertion is done : if two leobject are stored in the same
    #collection they share the same uid
    #
    #@param target LeObject subclass (no instance) : Target class
    #@param relational_filters : same composition thant filters except that
    #@return a struct as described above
    @classmethod
    def __prepare_relational_filters(cls, target, relational_filters):
        # We are going to regroup relationnal filters by reference field
        # then by collection
        rfilters = dict()
        for (fname, rfields), op, value in relational_filters:
            if fname not in rfilters:
                rfilters[fname] = dict()
            rfilters[fname] = dict()
            # Stores the representative leobject for associated to a collection
            # name
            leo_collname = dict()
            # WARNING ! Here we assert that all leobject that are stored
            # in a same collection are identified by the same field
            for leobject, rfield in rfields.items():
                #here we are filling a dict with leobject as index but
                #we are doing a UNIQ on collection name
                cur_collname = object_collection_name(leobject)
                if cur_collname not in collnames:
                    leo_collname[cur_collame] = leobject
                    rfilters[fname][leobject] = dict()
                #Fecthing the collection's representative leobject
                repr_leo = leo_collname[cur_collname]

                if rfield not in rfilters[fname][repr_leo]:
                    rfilters[fname][repr_leo][rfield] = list()
                rfilters[fname][repr_leo][rfield].append((op, value))
        return rfilters
    
    ##@brief Convert lodel2 filters to pymongo conditions
    #@param filters list : list of lodel filters
    #@return dict representing pymongo conditions
    @classmethod
    def __filters2mongo(cls, filters):
        res = dict()
        for fieldname, op, value in filters:
            oop = op
            ovalue = value
            op, value = cls.__op_value_conv(op, value)
            if fieldname not in res:
                res[fieldname] = dict()
            if op in res[fieldname]:
                logger.warn("Dropping condition : '%s %s %s'" % (
                    fieldname, op, value))
            else:
                res[fieldname][op] = value
        return res


    ##@brief Convert lodel2 operator and value to pymongo struct
    #
    #Convertion is done using MongoDbDatasource::lodel2mongo_op_map
    #@param op str : take value in LeFilteredQuery::_query_operators
    #@param value mixed : the value
    #@return a tuple(mongo_op, mongo_value)
    @classmethod
    def __op_value_conv(cls, op, value):
        if op not in cls.lodel2mongo_op_map:
            msg = "Invalid operator '%s' found" % op
            raise MongoDbDataSourceError(msg)
        mongop = cls.lodel2mongo_op_map[op]
        mongoval = value
        #Converting lodel2 wildcarded string into a case insensitive
        #mongodb re
        if mongop in cls.mon_op_re:
            #unescaping \
            mongoval = value.replace('\\\\','\\')
            if not mongoval.startswith('*'):
                mongoval = '^'+mongoval
            #For the end of the string it's harder to detect escaped *
            if not (mongoval[-1] == '*' and mongoval[-2] != '\\'):
                mongoval += '$'
            #Replacing every other unescaped wildcard char
            mongoval = cls.wildcard_re.sub('.*', mongoval)
            mongoval = {'$regex': mongoval, '$options': 'i'}
        return (op, mongoval)

    ##@brief Convert a list of tuple(OP, VALUE) into a pymongo filter dict
    #@return a dict with mongo op as key and value as value...
    @classmethod
    def __op_value_listconv(cls, op_value_list):
        result = dict()
        for op, value in op_value_list:
            mongop, mongoval = cls.__op_value_conv(op, value)
            if mongop in result:
                warnings.warn("Duplicated value given for a single \
field/operator couple in a query. We will keep only the first one")
            else:
                result[mongop] = mongoval
        return result

