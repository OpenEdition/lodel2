#-*- coding: utf-8 -*-

from .leobject import LeObject


class LeQueryError(Exception):
    pass


class LeQuery(object):

    ## @brief The datasource object used for this query
    _datasource = None

    ## @brief The available operators used in query definitions
    _query_operators = ['=', '<=', '>=', '!=', '<', '>', ' in ', ' not in ', ' like ', ' not like ']

    def __init__(self, target_class):
        if not issubclass(target_class, LeObject):
            raise TypeError("target class has to be a child class of LeObject")
        self._target_class = target_class


class LeInsertQuery(LeQuery):
    action = 'insert'

    def __init__(self, target_class, datas, classname=None):
        targeted_class = target_class if classname is None else LeObject.name2class(classname)
        if not targeted_class:
            raise LeQueryError('Error when inserting', {'error': ValueError("The class '%s' was not found" % classname)})

        super().__init__(targeted_class)
        self.datas = datas

    # @todo Reactivate the LodelHooks call when this class is implemented
    def execute(self):
        datas = self.datas  # TODO : replace with LodelHooks.call_hook('leapi_insert_pre', self._target_class, self.datas)
        ret = self.__insert(**datas)
        # ret = LodelHook.call_hook('leapi_insert_post', self._target_class, ret)
        return ret

    def __insert(self):
        insert_datas = self._target_class.prepare_datas(self.datas, complete=True, allow_internal=True)
        return self._datasource.insert(self._target_class, **insert_datas)


class LeFilteredQuery(LeQuery):

    def __init__(self, target_class):
        super().__init__(target_class)


class LeGetQuery(LeFilteredQuery):

    def __init__(self, target_class, target_uid, query_filters, field_list=None, order=None, group=None, limit=None, offset=0, instanciate=True):
        super().__init__(target_class)
        self.query_filters = query_filters
        self.default_field_list = []
        self.field_list = field_list if field_list is not None else self._target_class.fieldnames()
        self.order = order
        self.group = group
        self.limit = limit
        self.offset = offset
        self.instanciate = instanciate
        self.target_object = None  # TODO get an instance of the target_class using a unique id

    def execute(self):
        datas = self.datas  # TODO : replace with LodelHook.call_hook('leapi_get_pre', self.target_object, self.datas)
        ret = self.__get(**datas)
        # ret = LodelHook.call_hook('leapi_get_post', self.target_object, ret)
        return ret

    def __get(self, **kwargs):
        field_list = self.__prepare_field_list(self.field_list)  #TODO implement the prepare_field_list method

        # checks the limit and offset values
        if self.limit is not None and self.limit <= 0:
            raise ValueError('Invalid limit given')

        if self.offset is not None and self.offset < 0:
            raise ValueError('Invalid offset given : %d' % self.offset)

        results = self._datasource.select()  # TODO add the correct arguments for the datasource's method call
        return results

    def __prepare_field_list(self):
        pass

    def __prepare_filters(self):
        pass

    def __prepare_order(self):
        pass

    def __prepare_groups(self):
        pass


class LeUpdateQuery(LeFilteredQuery):

    def __init__(self, target_class, target_uid, query_filters):
        super().__init__(target_class)
        self.query_filters = query_filters
        self.target_uid = target_uid
        self.target_object = None # TODO get an instance of the target_class using a unique id

    def execute(self):
        # LodelHook.call_hook('leapi_update_pre', self.target_object, None)
        ret = self._update()
        # ret = LodelHook.call_hook('leapi_update_post', self.target_object, ret)
        return ret

    ## @brief calls the datasource's update method and the corresponding hooks
    # @return bool
    # @TODO change the behavior in case of error in the update process
    def __update(self):
        updated_datas = self.__prepare()
        ret = self._datasource.update(self.target_uid, **updated_datas)  # TODO add the correct arguments for the datasource's method call
        if ret == 1:
            return True
        else:
            return False

    ## @brief prepares the query_filters to be used as argument for the datasource's update method
    def __prepare(self):
        pass


class LeDeleteQuery(LeFilteredQuery):

    def __init__(self, target_class, target_uid, query_filters):
        super().__init__(self._target_class)
        self.target_uid = target_uid
        self.query_filters = query_filters

    def execute(self):
        # LodelHook.call_hook('leapi_delete_pre', self.target_uid, None)
        ret = self._delete()
        # ret = LodelHook.call('leapi_delete_post', self.target_object, ret)
        return ret

    def _delete(self):
        delete_datas = self.__prepare()
        ret = self._datasource.delete(self.target_uid, **delete_datas)
        return ret

    def __prepare(self):
        # TODO add the checks on the query_filters if needed
        pass