# -*- coding: utf-8 -*-

import os
import logging as logger

import sqlalchemy as sql

from Database.sqlwrapper import SqlWrapper

class SqlQueryBuilder():

    def __init__(self, sqlwrapper, table):
        if not type(sqlwrapper) is SqlWrapper:
             logger.error("Unable to instanciate, bad argument...")
             raise TypeError('Excepted a SqlWrapper not a '+str(type(sqlwrapper)))
        self.table = table
        self.sqlwrapper = sqlwrapper
        self.proxy = None


    def Select(self, arg):
        """ Alias for select clause
            @param arg iterable: arg must be a Python list or other iterable and contain eather table name/type or colum/literal_column
        """

        self.proxy = sql.select(arg)
        return self.proxy

    def Where(self, arg):
        """ Alias for where clause
            @param arg SQL expression object or string
        """
        self.proxy = self.proxy.where(arg)

    def From(self, arg):
        """ Alias for select_from clause
            @param arg Table or table('tablename') or join clause
        """
        self.proxy = self.proxy.select_from(arg)

    def Update(self):
        self.proxy = self.table.update()

    def Insert(self):
        self.proxy = self.table.insert()

    def Delete(self):
        self.proxy = self.proxy.delete()

    def Value(self, arg):
        """
        Allow you to specifies the VALUES or SET clause of the statement.
        @param arg: VALUES or SET clause
        """
        self.proxy = self.proxy.values(arg)

    def Execute(self):
        """
        Execute the sql query constructed in the proxy and return the result.
        If no query then return False.
        @return: query result on success else False
        """
        if(self.proxy.__str__().split() == 'SELECT'):
            return self.sqlwrapper.rconn.execute(self.proxy)
        elif(self.proxy is not None):
            return self.sqlwrapper.wconn.execute(self.proxy)
        else:
            return False



