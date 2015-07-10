# -*- coding: utf-8 -*-
import os
import logging as logger

import sqlalchemy as sqla
from django.conf import settings

import EditorialModel

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

ENGINES = {
    'mysql': {
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

sql_config = settings.LODEL2SQLWRAPPER


## Returns an engine given dbconf name
#
# @param ename str: name of an item in django.conf.settings.LODEL2SQLWRAPPER['db']
# @param sqlaloggin None|bool: If None leave default value, if true activate sqlalchemy logging
# @return SqlAlchemy engine
def get_engine(ename='default', sqlalogging=None):
    # Loading confs
    cfg = sql_config['db'][ename]

    edata = ENGINES[cfg['ENGINE']]  # engine infos
    conn_str = ""

    if cfg['ENGINE'] == 'sqlite':
        #SQLite connection string
        conn_str = '%s+%s:///%s' % (cfg['ENGINE'], edata['driver'], cfg['NAME'])
    else:
        #MySQL and PostgreSQL connection string
        user = cfg['USER']
        user += (':' + cfg['PASSWORD'] if 'PASSWORD' in cfg else '')

        if 'HOST' not in cfg:
            logger.info('Not HOST in configuration, using localhost')
            host = 'localhost'
        else:
            host = cfg['HOST']

        host += (':' + cfg['PORT'] if 'PORT' in cfg else '')
        conn_str = '%s+%s://' % (cfg['ENGINE'], edata['driver'])
        conn_str += '%s@%s/%s' % (user, host, cfg['NAME'])

    ret = sqla.create_engine(conn_str, encoding=edata['encoding'], echo=sqlalogging)
    logger.debug("Getting engine :" + str(ret))

    return ret


## Return a sqlalchemy.MetaData object
# @param engine sqlalchemy.engine : A sqlalchemy engine
# @return an sql alechemy MetaData instance bind to engine
def meta(engine):
    res = sqla.MetaData(bind=engine)
    res.reflect(bind=engine)
    return res


## Return an sqlalchemy table given an EmComponent child class
# @warning Except a class type not an instance
# @param cls : An EmComponent child class
# @return An sqlalchemy table
# @throw TypeError if em_instance is an EmComponent  or not an EmComponent child class (or an instance)
# @todo Move this function as an instance method ?
def get_table(self):
    if not issubclass(self.__class__, EditorialModel.components.EmComponent) or self.table is None:
        raise TypeError("Excepting an EmComponent child class not an " + str(self.__class__))
    engine = self.db_engine
    return sqla.Table(self.table, meta(engine))


## This function is intended to execute ddl defined in sqlalter
# @warning There is a dirty workaround here, DDL should returns only one query, but DropColumn for sqlite has to return 4 queries (rename, create, insert, drop). There is a split on the compiled SQL to extract and execute one query at a time
# @param ddl DDLElement: Can be an Database.sqlalter.DropColumn Database.sqlalter.AddColumn or Database.sqlalter.AlterColumn
# @param db_engine: A database engine
# @return True if success, else False
def ddl_execute(ddl, db_engine):
    conn = db_engine.connect()
    req = str(ddl.compile(dialect=db_engine.dialect))
    queries = req.split(';')
    for query in queries:
        logger.debug("Executing custom raw SQL query : '" + query + "'")
        ret = conn.execute(query)
        if not bool(ret):
            return False
    conn.close()
    return True
