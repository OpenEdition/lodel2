# -*- coding: utf-8 -*-

import os
import logging as logger

import sqlalchemy as sql

from Database.sqlwrapper import SqlWrapper

class SqlObject(object):
    """ Object that make aliases with sqlalchemy
        
        Example usage of object that inherite from SqlObject :
        
        class foo(SlqObject,...):
            def __init__(self, ...):
                self.__class__.tname = 'foo_table'

        f = foo(...)
        req = f.where(f.col.id == 42)
        res = f.rexec(req)

        e = bar(...)
        req = f.join(e.col.id == f.col.id)
        res = f.rexec(req)

    """

    def __init__(self, tname):
        self.tname = tname

    @property
    def table(self):
        return sql.Table(self.tname, sql.MetaData())

    @property
    def col(self):
        return self.table.c
    
    @property
    def sel(self):
        return sql.select(self.table)

    @property
    def where(self):
        return self.sel.where

    @property
    def join(self):
        return self.sel.join

    @property
    def rconn(self):
        return SqlWrapper.rconn()

    @property
    def wconn(self):
        return SqlWrapper.wconn()

    def sFetchAll(self, sel):
        return self.rexec(sel).fetchall()

    def rexec(self, o):
        return self.rconn.execute(o)

    def wexec(self, o):
        return self.wconn.execute(o)
