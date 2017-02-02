import os.path
from lodel.context import LodelContext

LodelContext.expose_module(globals(), {
    'lodel.plugin.datasource_plugin': ['AbstractDatasource', 'DatasourcePlugin'],
    'lodel.logger': 'logger',
    'lodel.exceptions': ['LodelFatalError'],
    'lodel.settings': 'Settings'})

from .fs_utils import *
from .specs import check as check_leo
from .exceptions import *


##@brief This datasource handles site creation
#@note Filters evaluation is forwarded to child datasource using our select
#method. Not optimized but much simple
class Datasource(AbstractDatasource):
    
    ##@brief Constructor
    #
    #Handles child datasource instanciation
    #@param db_datasource str : datasource identifier
    #@param db_datasource_ro str : read only datasource identitifer
    def __init__(self, db_datasource, db_datasource_ro = None):
        if db_datasource_ro is None:
            db_datasource = db_datasource_ro
        self._child_ds = DatasourcePlugin.init_datasource(
            db_datasource, False)
        self._child_ds_ro = DatasourcePlugin.init_datasource(
            db_datasource, True)
        pass
    
    ##@brief Checks that given emcomponent is compatible with datasource
    #behavior
    #@warning 100% hardcoded checks on leo name fieldnames & types
    #@param emcomp LeObject subclass (or instance)
    #@throws LodelFatalError if not compatible
    @staticmethod
    def __assert_good_leo(leo):
        res, reason = check_leo(leo)
        if not res:
            msg = 'Bad leo given : %s because %s' % (leo, reason)
            logger.fatal(msg)
            raise LodelFatalError(msg)

    ##@brief Provide a new uniq numeric ID
    #@param emcomp LeObject subclass (not instance) : To know on wich things we
    #have to be uniq
    #@return an integer
    def new_numeric_id(self, emcomp):
        self.__assert_good_leo(emcomp)
        return self._child_ds.new_numeric_id(emcomp)
    
    ##@brief returns a selection of documents from the datasource
    #@note Simply forwarded to ro child datasource
    #@param target Emclass
    #@param field_list list
    #@param filters list : List of filters
    #@param rel_filters list : List of relational filters
    #@param order list : List of column to order. ex: order = [('title', 'ASC'),]
    #@param group list : List of tupple representing the column to group together. ex: group = [('title', 'ASC'),]
    #@param limit int : Number of records to be returned
    #@param offset int: used with limit to choose the start record
    #@param instanciate bool : If true, the records are returned as instances, else they are returned as dict
    #@return list
    def select(self, target, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0,
               instanciate=True):
        return self._child_ds_ro.select(
            target, field_list, rel_filters, order, group, limit, offset)

    ##@brief Deletes records according to given filters
    #@note lazy filters evaluation implementation : to evaluate filters &
    #rel_filters we run self.select using them
    #@param target Emclass : class of the record to delete
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@return int : number of deleted records
    def delete(self, target, filters, relational_filters):
        shortnames = self.select(
            target,
            ['shortname'],
            filters,
            relational_filters)
        for shortname in [ item['shortname'] for item in shortnames]:
            purge(shortname)
        return self._child_ds.delete(target, filters, relational_filters)

    ## @brief updates records according to given filters
    #
    #@note lazy filters evaluation implementation : to evaluate filters &
    #rel_filters we run self.select using them
    #@note shortname updates are forbidden
    #@param target Emclass : class of the object to update
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@param upd_datas dict : datas to update (new values)
    #@return int : Number of updated records
    def update(self, target, filters, relational_filters, upd_datas):
        if 'shortname' in upd_datas:
            raise LodelSiteDatasourceError('Not able to update the \
shortname, its a site identifier. The good way of doing this is to copy \
existing site with a new name')
        
        datas = self.select(
            target,
            ['shortname', 'groups', 'extensions'],
            filters,
            relational_filters)

        for data in datas:
            if 'groups' in upd_datas:
                groups = upd_datas['groups']
            else:
                groups = data['groups']
            if 'extensions' in upd_datas:
                extensions = upd_datas['extensions']
            else:
                extensions = data['extensions']

            update_conf(**{
                'sitename': data['shortname'],
                'groups': groups,
                'extensions': extensions})
        
        return self._child_ds.update(
            target, filters, relational_filters, upd_datas)

    ##@brief Inserts a record in a given collection
    #@param target Emclass : class of the object to insert
    #@param new_datas dict : datas to insert
    #@return the inserted uid
    def insert(self, target, new_datas):
        self.__assert_good_leo(target)
        if site_exists(new_datas['shortname']):
            raise LodelSiteDatasourceError('A site with "%s" as shortname \
allready exists' % (new_datas['shortname']))
        site_directories_creation(new_datas['shortname'])
        generate_conf(
            new_datas['shortname'],
            new_datas['groups'],
            new_datas['extensions'])
        return self._child_ds.insert(target, new_datas)

    ## @brief Inserts a list of records in a given collection
    #@note Here is a simple implementation : a for loop triggering
    #insert() calls
    # @param target Emclass : class of the objects inserted
    # @param datas_list list : list of dict
    # @return list : list of the inserted records' ids
    def insert_multi(self, target, datas_list):
        res = []
        for new_datas in datas_list:
            res.append(self.insert(target, datas))
        return res       


