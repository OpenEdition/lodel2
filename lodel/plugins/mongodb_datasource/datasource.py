object# -*- coding: utf-8 -*-

import re
import warnings
import copy
import functools
from bson.son import SON
from collections import OrderedDict
import pymongo
from pymongo.errors import BulkWriteError

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.leapi.leobject': ['CLASS_ID_FIELDNAME'],
    'lodel.leapi.datahandlers.base_classes': ['Reference', 'MultipleRef'],
    'lodel.exceptions': ['LodelException', 'LodelFatalError'],
    'lodel.plugin.datasource_plugin': ['AbstractDatasource']})

from . import utils
from .exceptions import *
from .utils import object_collection_name, collection_name, \
    MONGODB_SORT_OPERATORS_MAP, connection_string, mongo_fieldname


##@brief Datasource class
#@ingroup plugin_mongodb_datasource
class MongoDbDatasource(AbstractDatasource):

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
    #@param read_only bool : If True the Datasource is for read only, else the
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
            username, password, db_name, self.__read_only)

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
            target, field_list = [tuid], filters = [],
            order=[(tuid, 'DESC')], limit = 1)
        if len(results) == 0:
            return 1
        return results[0][tuid]+1

    ##@brief returns a selection of documents from the datasource
    #@param target Emclass
    #@param field_list list
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@param order list : List of column to order. ex: order =
    #[('title', 'ASC'),]
    #@param group list : List of tupple representing the column used as
    #"group by" fields. ex: group = [('title', 'ASC'),]
    #@param limit int : Number of records to be returned
    #@param offset int: used with limit to choose the start record
    #@return list
    #@todo Implement group for abstract LeObject childs
    def select(self, target, field_list, filters = None,
            relational_filters=None, order=None, group=None, limit=None,
            offset=0):
        if target.is_abstract():
            #Reccursiv calls for abstract LeObject child
            results =  self.__act_on_abstract(target, filters,
                relational_filters, self.select, field_list = field_list,
                order = order, group = group, limit = limit)

            #Here we may implement the group
            #If sorted query we have to sort again
            if order is not None:
                key_fun = functools.cmp_to_key(
                    self.__generate_lambda_cmp_order(order))
                results = sorted(results, key=key_fun)
            #If limit given apply limit again
            if offset > len(results):
                results = list()
            else:
                if limit is not None:
                    if limit + offset > len(results):
                        limit = len(results)-offset-1
                    results = results[offset:offset+limit]
            return results
        # Default behavior
        if filters is None:
            filters = list()
        if relational_filters is None:
            relational_filters = list()

        collection_name = object_collection_name(target)
        collection = self.database[collection_name]

        query_filters = self.__process_filters(
            target, filters, relational_filters)

        query_result_ordering = None
        if order is not None:
            query_result_ordering = utils.parse_query_order(order)

        if group is None:
            if field_list is None:
                field_list = dict()
            else:
                f_list=dict()
                for fl in field_list:
                    f_list[fl] = 1
                field_list = f_list
            field_list['_id'] = 0
            cursor = collection.find(
                spec = query_filters,
                fields=field_list,
                skip=offset,
                limit=limit if limit != None else 0,
                sort=query_result_ordering)
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
            if field_list is not None:
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

        results = list()
        for document in cursor:
            results.append(document)

        return results

    ##@brief Deletes records according to given filters
    #@param target Emclass : class of the record to delete
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@return int : number of deleted records
    def delete(self, target, filters, relational_filters):
        if target.is_abstract():
            logger.debug("Delete called on %s filtered by (%s,%s). Target is \
abstract, preparing reccursiv calls" % (target, filters, relational_filters))
            #Deletion with abstract LeObject as target (reccursiv calls)
            return self.__act_on_abstract(target, filters,
                relational_filters, self.delete)
        logger.debug("Delete called on %s filtered by (%s,%s)." % (
            target, filters, relational_filters))
        #Non abstract beahavior
        mongo_filters = self.__process_filters(
            target, filters, relational_filters)
        #Updating backref before deletion
        self.__update_backref_filtered(target, filters, relational_filters,
            None)
        res = self.__collection(target).remove(mongo_filters)
        return res['n']

    ##@brief updates records according to given filters
    #@param target Emclass : class of the object to insert
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@param upd_datas dict : datas to update (new values)
    #@return int : Number of updated records
    def update(self, target, filters, relational_filters, upd_datas):
        self._data_cast(upd_datas)
        #fetching current datas state
        mongo_filters = self.__process_filters(
            target, filters, relational_filters)
        old_datas_l = self.__collection(target).find(
            mongo_filters)
        old_datas_l = list(old_datas_l)
        #Running update
        res = self.__update_no_backref(target, filters, relational_filters,
            upd_datas)
        #updating backref
        self.__update_backref_filtered(target, filters, relational_filters,
            upd_datas, old_datas_l)
        return res

    ##@brief Designed to be called by backref update in order to avoid
    #infinite updates between back references
    #@see update()
    def __update_no_backref(self, target, filters, relational_filters,
            upd_datas):
        logger.debug("Update called on %s filtered by (%s,%s) with datas \
%s" % (target, filters, relational_filters, upd_datas))
        if target.is_abstract():
            #Update using abstract LeObject as target (reccursiv calls)
            return self.__act_on_abstract(target, filters,
                relational_filters, self.update, upd_datas = upd_datas)
        #Non abstract beahavior
        mongo_filters = self.__process_filters(
            target, filters, relational_filters)
        self._data_cast(upd_datas)
        mongo_arg = {'$set': upd_datas }
        res = self.__collection(target).update(mongo_filters, mongo_arg)
        return res['n']

    ## @brief Inserts a record in a given collection
    # @param target Emclass : class of the object to insert
    # @param new_datas dict : datas to insert
    # @return the inserted uid
    def insert(self, target, new_datas):
        self._data_cast(new_datas)
        logger.debug("Insert called on %s with datas : %s"% (
            target, new_datas))
        uidname = target.uid_fieldname()[0] #MULTIPLE UID BROKEN HERE
        if uidname not in new_datas:
            raise MongoDataSourceError("Missing UID data will inserting a new \
%s" % target.__class__)
        res = self.__collection(target).insert(new_datas)
        self.__update_backref(target, new_datas[uidname], None, new_datas)
        return str(res)

    ## @brief Inserts a list of records in a given collection
    # @param target Emclass : class of the objects inserted
    # @param datas_list list : list of dict
    # @return list : list of the inserted records' ids
    def insert_multi(self, target, datas_list):
        for datas in datas_list:
            self._data_cast(datas)
        res = self.__collection(target).insert_many(datas_list)
        for new_datas in datas_list:
            self.__update_backref(target, None, new_datas)
            target.make_consistency(datas=new_datas)
        return list(res.inserted_ids)

    ##@brief Update backref giving an action
    #@param target leObject child class
    #@param filters
    #@param relational_filters,
    #@param new_datas None | dict : optional new datas if None mean we are deleting
    #@param old_datas_l None | list : if None fetch old datas from db (usefull
    #when modifications are made on instance before updating backrefs)
    #@return nothing (for the moment
    def __update_backref_filtered(self, target,
            filters, relational_filters, new_datas = None, old_datas_l = None):
        #Getting all the UID of the object that will be deleted in order
        #to update back_references
        if old_datas_l is None:
            mongo_filters = self.__process_filters(
                target, filters, relational_filters)
            old_datas_l = self.__collection(target).find(
                mongo_filters)
            old_datas_l = list(old_datas_l)

        uidname = target.uid_fieldname()[0] #MULTIPLE UID BROKEN HERE
        for old_datas in old_datas_l:
            self.__update_backref(
                target, old_datas[uidname], old_datas, new_datas)

    ##@brief Update back references of an object
    #@ingroup plugin_mongodb_bref_op
    #
    #old_datas and new_datas arguments are set to None to indicate
    #insertion or deletion. Calls examples :
    #@par LeObject insert __update backref call
    #<pre>
    #Insert(datas):
    #  self.make_insert(datas)
    #  self.__update_backref(self.__class__, None, datas)
    #</pre>
    #@par LeObject delete __update backref call
    #Delete()
    #  old_datas = self.datas()
    #  self.make_delete()
    #  self.__update_backref(self.__class__, old_datas, None)
    #@par LeObject update __update_backref call
    #<pre>
    #Update(new_datas):
    #  old_datas = self.datas()
    #  self.make_udpdate(new_datas)
    #  self.__update_backref(self.__class__, old_datas, new_datas)
    #</pre>
    #
    #@param target LeObject child classa
    #@param tuid mixed : The target UID (the value that will be inserted in
    #back references)
    #@param old_datas dict : datas state before update
    #@param new_datas dict : datas state after the update process
    #retun None
    def __update_backref(self, target, tuid, old_datas, new_datas):
        #upd_dict is the dict that will allow to run updates in an optimized
        #way (or try to help doing it)
        #
        #It's struct looks like :
        # { LeoCLASS : {
        #       UID1: (
        #           LeoINSTANCE,
        #           { fname1 : value, fname2: value }),
        #       UID2 (LeoINSTANCE, {fname...}),
        #       },
        #   LeoClass2: {...
        #
        upd_dict = {}
        for fname, fdh in target.reference_handlers().items():
            oldd = old_datas is not None and fname in old_datas and \
                (not hasattr(fdh, 'default') or old_datas[fname] != fdh.default) \
                and not old_datas[fname] is None
            newd = new_datas is not None and fname in new_datas and \
                (not hasattr(fdh, 'default') or new_datas[fname] != fdh.default) \
                and not new_datas[fname] is None
            if (oldd and newd and old_datas[fname] == new_datas[fname])\
                    or not(oldd or newd):
                #No changes or not concerned
                continue
            bref_cls = fdh.back_reference[0]
            bref_fname = fdh.back_reference[1]
            if not fdh.is_singlereference():
                #fdh is a multiple ref. So the update preparation will be
                #divided into two loops :
                #- one loop for deleting old datas
                #- one loop for inserting updated datas
                #
                #Preparing the list of values to delete or to add
                if newd and oldd:
                    old_values = old_datas[fname]
                    new_values = new_datas[fname]
                    to_del = [  val
                                for val in old_values
                                if val not in new_values]
                    to_add = [  val
                                for val in new_values
                                if val not in old_values]
                elif oldd and not newd:
                    to_del = old_datas[fname]
                    to_add = []
                elif not oldd and newd:
                    to_del = []
                    to_add = new_datas[fname]
                #Calling __back_ref_upd_one_value() with good arguments
                for vtype, vlist in [('old',to_del), ('new', to_add)]:
                    for value in vlist:
                        #fetching backref infos
                        bref_infos = self.__bref_get_check(
                            bref_cls, value, bref_fname)
                        #preparing the upd_dict
                        upd_dict = self.__update_backref_upd_dict_prepare(
                            upd_dict, bref_infos, bref_fname, value)
                        #preparing updated bref_infos
                        bref_cls, bref_leo, bref_dh, bref_value = bref_infos
                        bref_infos = (bref_cls, bref_leo, bref_dh,
                            upd_dict[bref_cls][value][1][bref_fname])
                        vdict = {vtype: value}
                        #fetch and store updated value
                        new_bref_val = self.__back_ref_upd_one_value(
                            fname, fdh, tuid, bref_infos, **vdict)
                        upd_dict[bref_cls][value][1][bref_fname] = new_bref_val
            else:
                #fdh is a single ref so the process is simpler, we do not have
                #to loop and we may do an update in only one
                #__back_ref_upd_one_value() call by giving both old and new
                #value
                vdict = {}
                if oldd:
                    vdict['old'] = old_datas[fname]
                    uid_val = vdict['old']
                if newd:
                    vdict['new'] = new_datas[fname]
                    if not oldd:
                        uid_val = vdict['new']
                #Fetching back ref infos
                bref_infos = self.__bref_get_check(
                    bref_cls, uid_val, bref_fname)
                #prepare the upd_dict
                upd_dict = self.__update_backref_upd_dict_prepare(
                    upd_dict, bref_infos, bref_fname, uid_val)
                #forging update bref_infos
                bref_cls, bref_leo, bref_dh, bref_value = bref_infos
                bref_infos = (bref_cls, bref_leo, bref_dh,
                        upd_dict[bref_cls][uid_val][1][bref_fname])
                #fetche and store updated value
                new_bref_val = self.__back_ref_upd_one_value(
                    fname, fdh, tuid, bref_infos, **vdict)
                upd_dict[bref_cls][uid_val][1][bref_fname] = new_bref_val
        #Now we've got our upd_dict ready.
        #running the updates
        for bref_cls, uid_dict in upd_dict.items():
            for uidval, (leo, datas) in uid_dict.items():
                #MULTIPLE UID BROKEN 2 LINES BELOW
                self.__update_no_backref(
                    leo.__class__, [(leo.uid_fieldname()[0], '=', uidval)],
                    [], datas)

    ##@brief Utility function designed to handle the upd_dict of
    #__update_backref()
    #
    #Basically checks if a key exists at some level, if not create it with
    #the good default value (in most case dict())
    #@param upd_dict dict : in & out args modified by reference
    #@param bref_infos tuple : as returned by __bref_get_check()
    #@param bref_fname str : name of the field in referenced class
    #@param uid_val mixed : the UID of the referenced object
    #@return the updated version of upd_dict
    @staticmethod
    def __update_backref_upd_dict_prepare(upd_dict,bref_infos, bref_fname,
            uid_val):
        bref_cls, bref_leo, bref_dh, bref_value = bref_infos
        if bref_cls not in upd_dict:
            upd_dict[bref_cls] = {}
        if uid_val not in upd_dict[bref_cls]:
            upd_dict[bref_cls][uid_val] = (bref_leo, {})
        if bref_fname not in upd_dict[bref_cls][uid_val]:
            upd_dict[bref_cls][uid_val][1][bref_fname] = bref_value
        return upd_dict


    ##@brief Prepare a one value back reference update
    #@param fname str : the source Reference field name
    #@param fdh DataHandler : the source Reference DataHandler
    #@param tuid mixed : the uid of the Leo that make reference to the backref
    #@param bref_infos tuple : as returned by __bref_get_check() method
    #@param old mixed : (optional **values) the old value
    #@param new mixed : (optional **values) the new value
    #@return the new back reference field value
    def __back_ref_upd_one_value(self, fname, fdh, tuid, bref_infos, **values):
        bref_cls, bref_leo, bref_dh, bref_val = bref_infos
        oldd = 'old' in values
        newdd = 'new' in values
        if bref_val is None:
            bref_val = bref_dh.empty()
        if not bref_dh.is_singlereference():
            if oldd and newdd:
                if tuid not in bref_val:
                    raise MongoDbConsistencyError("The value we want to \
delete in this back reference update was not found in the back referenced \
object : %s. Value was : '%s'" % (bref_leo, tuid))
                return bref_val
            elif oldd and not newdd:
                #deletion
                old_value = values['old']
                if tuid not in bref_val:
                    raise MongoDbConsistencyError("The value we want to \
delete in this back reference update was not found in the back referenced \
object : %s. Value was : '%s'" % (bref_leo, tuid))
                if isinstance(bref_val, tuple):
                    bref_val = set(bref_val)
                if isinstance(bref_val, set):
                    bref_val -= set([tuid])
                else:
                    del(bref_val[bref_val.index(tuid)])
            elif not oldd and newdd:
                if tuid in bref_val:
                    raise MongoDbConsistencyError("The value we want to \
add in this back reference update was found in the back referenced \
object : %s. Value was : '%s'" % (bref_leo, tuid))
                if isinstance(bref_val, tuple):
                    bref_val = set(bref_val)
                if isinstance(bref_val, set):
                    bref_val |= set([tuid])
                else:
                    bref_val.append(tuid)
        else:
            #Single value backref
            if oldd and newdd:
                if bref_val != tuid:
                    raise MongoDbConsistencyError("The backreference doesn't \
have expected value. Expected was %s but found %s in %s" % (
                        tuid, bref_val, bref_leo))
                return bref_val
            elif oldd and not newdd:
                #deletion
                if not hasattr(bref_dh, "default"):
                    raise MongoDbConsistencyError("Unable to delete a \
value for a back reference update. The concerned field don't have a default \
value : in %s field %s" % (bref_leo,fname))
                bref_val = getattr(bref_dh, "default")
            elif not oldd and newdd:
                bref_val = tuid
        return bref_val

    ##@brief Fetch back reference informations
    #@warning thank's to __update_backref_act() this method is useless
    #@param bref_cls LeObject child class : __back_reference[0]
    #@param uidv mixed : UID value (the content of the reference field)
    #@param bref_fname str : the name of the back_reference field
    #@return tuple(bref_class, bref_LeObect_instance, bref_datahandler,
    #bref_value)
    #@throw MongoDbConsistencyError when LeObject instance not found given
    #uidv
    #@throw LodelFatalError if the back reference field is not a Reference
    #subclass (major failure)
    def __bref_get_check(self, bref_cls, uidv, bref_fname):
        bref_leo = bref_cls.get_from_uid(uidv)
        if bref_leo is None:
            raise MongoDbConsistencyError("Unable to get the object we make \
reference to : %s with uid = %s" % (bref_cls, repr(uidv)))
        bref_dh = bref_leo.data_handler(bref_fname)
        if not bref_dh.is_reference():
            raise LodelFatalError("Found a back reference field that \
is not a reference : '%s' field '%s'" % (bref_leo, bref_fname))
        bref_val = bref_leo.data(bref_fname)
        return (bref_leo.__class__, bref_leo, bref_dh, bref_val)

    ##@brief Act on abstract LeObject child
    #
    #This method is designed to be called by insert, select and delete method
    #when they encounter an abtract class
    #@param target LeObject child class
    #@param filters
    #@param relational_filters
    #@param act function : the caller method
    #@param **kwargs other arguments
    #@return sum of results (if it's an array it will result in a concat)
    #@todo optimization implementing a cache for __bref_get_check()
    def __act_on_abstract(self,
        target, filters, relational_filters, act, **kwargs):

        logger.debug("Abstract %s, running reccursiv select \
on non abstract childs" % act.__name__)
        result = list() if act == self.select else 0
        if not target.is_abstract():
            target_childs = [target]
        else:
            target_childs = [tc for tc in target.child_classes()
                if not tc.is_abstract()]
        for target_child in target_childs:
            logger.debug(
                "Abstract %s on %s" % (act.__name__, target_child.__name__))
            #Add target_child to filter
            new_filters = copy.copy(filters)
            for i in range(len(filters)):
                fname, op, val = filters[i]
                if fname == CLASS_ID_FIELDNAME:
                    logger.warning("Dirty drop of filter : '%s %s %s'" % (
                        fname, op, val))
                    del(new_filters[i])
            new_filters.append(
                (CLASS_ID_FIELDNAME, '=',
                    collection_name(target_child.__name__)))
            result += act(
                target = target_child,
                filters = new_filters,
                relational_filters = relational_filters,
                **kwargs)
        return result

    ##@brief Connect to database
    #@note this method avoid opening two times the same connection using
    #MongoDbDatasource::_connections static attribute
    #@param username str
    #@param password str
    #@param ro bool : If True the Datasource is for read only, else the
    def __connect(self, username, password, db_name, ro):
        conn_string = connection_string(
            username = username, password = password,
            host = self.__db_infos['host'],
            port = self.__db_infos['port'],
            db_name = db_name,
            ro = ro)

        self.__conn_hash = conn_h = hash(conn_string)
        if conn_h in self._connections:
            self._connections[conn_h]['conn_count'] += 1
            return self._connections[conn_h]['db'][self.__db_infos['db_name']]
        else:
            logger.info("Opening a new connection to database")
            self._connections[conn_h] = {
                'conn_count': 1,
                'db': utils.connect(conn_string)}
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
        res = self.__filters2mongo(filters, target)
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
                deduped = set(res[fname]['$in']) & subq_results
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
                        rfilters[fname][leobject][rfield], target.field(fname))
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
        if relational_filters is None:
            relational_filters = []
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
                if cur_collname not in leo_collname:
                    leo_collname[cur_collname] = leobject
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
    def __filters2mongo(cls, filters, target):
        res = dict()
        eq_fieldname = [] #Stores field with equal comparison OP
        for fieldname, op, value in filters:
            oop = op
            ovalue = value
            op, value = cls.__op_value_conv(op, value, target.field(fieldname))
            if op == '=':
                eq_fieldname.append(fieldname)
                if fieldname in res:
                    logger.warning("Dropping previous condition. Overwritten \
by an equality filter")
                res[fieldname] = value
                continue
            if fieldname in eq_fieldname:
                logger.warning("Dropping condition : '%s %s %s'" % (
                    fieldname, op, value))
                continue

            if fieldname not in res:
                res[fieldname] = dict()
            if op in res[fieldname]:
                logger.warning("Dropping condition : '%s %s %s'" % (
                    fieldname, op, value))
            else:
                if op not in cls.lodel2mongo_op_map:
                    raise ValueError("Invalid operator : '%s'" % op)
                new_op = cls.lodel2mongo_op_map[op]
                res[fieldname][new_op] = value
        return res


    ##@brief Convert lodel2 operator and value to pymongo struct
    #
    #Convertion is done using MongoDbDatasource::lodel2mongo_op_map
    #@param op str : take value in LeFilteredQuery::_query_operators
    #@param value mixed : the value
    #@return a tuple(mongo_op, mongo_value)
    @classmethod
    def __op_value_conv(cls, op, value, dhdl):
        if op not in cls.lodel2mongo_op_map:
            msg = "Invalid operator '%s' found" % op
            raise MongoDbDataSourceError(msg)
        mongop = cls.lodel2mongo_op_map[op]
        mongoval = value
        #Converting lodel2 wildcarded string into a case insensitive
        #mongodb re
        if mongop in cls.mongo_op_re:
            if value.startswith('(') and value.endswith(')'):
                if (dhdl.cast_type is not None):
                    mongoval = [ dhdl.cast_type(item) for item in mongoval[1:-1].split(',') ]
                else:
                    mongoval = [ item for item in mongoval[1:-1].split(',') ]
        elif mongop == 'like':
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
    def __op_value_listconv(cls, op_value_list, dhdl):
        result = dict()
        for op, value in op_value_list:
            mongop, mongoval = cls.__op_value_conv(op, value, dhdl)
            if mongop in result:
                warnings.warn("Duplicated value given for a single \
field/operator couple in a query. We will keep only the first one")
            else:
                result[mongop] = mongoval
        return result

    ##@brief Generate a comparison function for post reccursion sorting in
    #select
    #@return a lambda function that take 2 dict as arguement
    @classmethod
    def __generate_lambda_cmp_order(cls, order):
        if len(order) == 0:
            return lambda a,b: 0
        glco = cls.__generate_lambda_cmp_order
        fname, cmpdir = order[0]
        order = order[1:]
        return lambda a,b: glco(order)(a,b) if a[fname] == b[fname] else (\
            1 if (a[fname]>b[fname] if cmpdir == 'ASC' else a[fname]<b[fname])\
            else -1)


    ##@brief Correct some datas before giving them to pymongo
    #
    #For example sets has to be casted to lise
    #@param datas
    #@return datas
    @classmethod
    def _data_cast(cls, datas):
        for dname in datas:
            if isinstance(datas[dname], set):
                #pymongo raises :
                #bson.errors.InvalidDocument: Cannot encode object: {...}
                #with sets
                datas[dname] = list(datas[dname])
        return datas
