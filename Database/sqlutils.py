# -*- coding: utf-8 -*-
import os
import re
import logging as logger

import sqlalchemy as sqla
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

ENGINES = {'mysql': {
                'driver': 'pymysql',
                'encoding': 'utf8'
            },
            'postgresql': {
                'driver': 'psycopg2',
                'encoding': 'utf8',
            },
            'sqlite': {
                'driver': 'pysqlite',
                'encoding': 'utf8',
            },
}

sqlcfg = settings.LODEL2SQLWRAPPER

## Return an engine given a dbconf name
# @param ename str: Its a name of an item in django.conf.settings.LODEL2SQLWRAPPER['db']
# @param sqlalogging None|bool : If None leave default value, if true activate sqlalchemy logging
# @return An sqlalchemy engine
def getEngine(ename = 'default', sqlalogging = None):
    """ Return a sqlalchemy engine
        @param read bool: If True return the read engine, else 
        return the write one
        @return a sqlachemy engine instance

        @todo Put the check on db config in SqlWrapper.checkConf()
    """
    #Loading confs
    cfg = sqlcfg['db'][ename]

    edata = ENGINES[cfg['ENGINE']] #engine infos
    conn_str = ""

    if cfg['ENGINE'] == 'sqlite':
        #Sqlite connection string
        conn_str = '%s+%s:///%s'%( cfg['ENGINE'],
            edata['driver'],
            cfg['NAME'])
    else:
        #Mysql and Postgres connection string
        user = cfg['USER']
        user += (':'+cfg['PASSWORD'] if 'PASSWORD' in cfg else '')
        
        if 'HOST' not in cfg:
            logger.info('Not HOST in configuration, using localhost')
            host = 'localhost'
        else:
            host = cfg['HOST']

        host += (':'+cfg['PORT'] if 'PORT' in cfg else '')

        conn_str = '%s+%s://'%(cfg['ENGINE'], edata['driver'])
        conn_str += '%s@%s/%s'%(user,host,cfg['NAME'])


    ret = sqla.create_engine(conn_str, encoding=edata['encoding'], echo=sqlalogging)

    logger.debug("Getting engine :"+str(ret))

    return ret

## Return a sqlalchemy.MetaData object
# @param engine sqlalchemy.engine : A sqlalchemy engine
# @return an sql alechemy MetaData instance bind to engine
def meta(engine):
    res = sqla.MetaData()
    res.reflect(bind=engine)
    return res

## Return an sqlalchemy table given an EmComponent child class
# @warning Except a class type not an instance
# @param em_class : An EmComponent child class
# @return An sqlalchemy table
# @throw TypeError if em_instance is an EmComponent  or not an EmComponent child class (or an instance)
def getTable(cls):
    from EditorialModel.components import EmComponent #dirty circula inclusion hack
    if not issubclass(cls, EmComponent) or cls.table == None:
        raise TypeError("Excepting an EmComponent child class not an "+str(cls))
    engine = cls.getDbE()
    return sqla.Table(cls.table, meta(engine))

def ddl_execute(ddl, db_engine):
    conn = db_engine.connect()
    req = str(ddl.compile(dialect=db_engine.dialect))
    logger.debug("Executing custom raw SQL query : '"+req+"'")
    ret = conn.execute(req)
    conn.close()
    return bool(ret)

