# -*- coding: utf-8 -*-
import os
import logging as logger

import sqlalchemy as sqla
from django.conf import settings

#Logger config
logger.getLogger().setLevel('DEBUG')
#To be able to use dango confs
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

class SqlWrapper(object):
    """ A wrapper class to sqlalchemy 
        Usefull to provide a standart API
    """

    ##Read Engine
    rengine = None
    ##Write Engine
    wengine = None

    ##Read connection
    rconn = None
    ##Write connection
    wconn = None

    ##Configuration dict alias for class access
    config=settings.LODEL2SQLWRAPPER
    ##SqlAlchemy logging
    sqla_logging = False

    def __init__(self, alchemy_logs=None):
        """ Instanciate a new SqlWrapper
            @param alchemy_logs bool: If true activate sqlalchemy logger
        """
        
        if (alchemy_logs != None and bool(alchemy_logs) != self.__class__.sqla_logging):
            #logging config changed for sqlalchemy
            self.__class__.restart()

        if not self.__class__.started():
            self.__class__.start()
        
        pass

    @classmethod
    def table(c, tname):
        """ Return a SqlAlchemy Table object
            @param o str: Table name
            @return a SqlAlchemy Table instance
        """
        if not isinstance(tname, str):
            raise TypeError("Excepting a str but got a "+str(type(name)))
        return sqla.Table(o, sqla.MetaData())

    @classmethod
    def connect(c,read = None):
        
        if read == None:
            return c.connect(True) and c.coonect(False)
        elif read:
            c.rconn = c.rengine.connect()
        else:
            c.wconn = c.wengine.connect()
        return True #TODO attention c'est pas checké...

    @classmethod   
    def conn(c, read=True):
        if read:
            res = c.rconn
        else:
            res = c.wconn

        if res == None:
            if not c.connect(read):
                raise RuntimeError('Unable to connect to Db')
            return c.conn(read)

        return c.rconn

    @classmethod
    def rc(c): return c.conn(True)
    @classmethod
    def wc(c): return c.conn(False)

    @classmethod
    def start(c, sqlalogging = None):
        """ Load engines
            Open connections to databases
            @param sqlalogging bool: overwrite class parameter about sqlalchemy logging
            @return False if already started
        """
        c.checkConf()
        if c.started():
            logger.warning('Starting SqlWrapper but it is allready started')
            return False

        c.rengine = c._getEngine(read=True, sqlalogging=None)
        c.wengine = c._getEngine(read=False, sqlalogging=None)
        return True

    @classmethod
    def stop(c): c.rengine = c.wengine = None; pass
    @classmethod
    def restart(c): c.stop(); c.start(); pass
    @classmethod
    def started(c): return (c.rengine != None and c.rengine != None)
    
    @classmethod
    def _sqllog(c,sqlalogging = None):
        return bool(sqlalogging) if sqlalogging != None else c.sqla_logging

    @classmethod
    def _getEngine(c, read=True, sqlalogging = None):
        """ Return a sqlalchemy engine
            @param read bool: If True return the read engine, else 
            return the write one
            @return a sqlachemy engine instance

            @todo Put the check on db config in SqlWrapper.checkConf()
        """
        #Loading confs
        connconf = 'dbread' if read else 'dbwrite'
        dbconf = connconf if connconf in c.config['db'] else 'default'

        if dbconf not in c.config['db']: #This check should not be here
            raise NameError('Configuration error no db "'+dbconf+'" in configuration files')
        
        cfg = c.config['db'][dbconf] #Database config
        
        edata = c.config['engines'][cfg['ENGINE']] #engine infos
        conn_str = cfg['ENGINE']+'+'+edata['driver']+'://'

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

        return sqla.create_engine(conn_str, encoding=edata['encoding'], echo=c._sqllog(sqlalogging))

    @classmethod
    def checkConf(c):
        """ Class method that check the configuration
            
            Configuration looks like
            - db (mandatory)
             - ENGINE (mandatory)
             - NAME (mandatory)
             - USER
             - PASSWORD
            - engines (mandatory)
             - driver (mandatory)
             - encoding (mandatory)
            - dbread (mandatory if no default db)
            - dbwrite (mandatory if no default db)
        """
        err = []
        if 'db' not in c.config:
            err.append('Missing "db" in configuration')
        else:
            if 'default' not in c.config['db']:
                if 'dbread' not in c.config:
                    err.append('Missing "dbread" in configuration and  no "default" db declared')
                if 'dbwrite' not in c.config:
                    err.append('Missing "dbwrite" in configuration and no "default" db declared')
            for dbname in c.config['db']:
                db = c.config['db'][dbname]
                if 'ENGINE' not in db:
                    err.append('Missing "ENGINE" in database "'+db+'"')
                else:
                    if db['ENGINE'] != 'sqlite' and 'USER' not in db:
                        err.append('Missing "USER" in database "'+db+'"')
                if 'NAME' not in db:
                    err.append('Missing "NAME" in database "'+db+'"')
        
        if len(c.config['engines']) == 0:
            err.append('Missing "engines" in configuration')
        for ename in c.config['engines']:
            engine = c.config['engines'][ename]
            if 'driver' not in engine:
                err.append('Missing "driver" in database engine "'+ename+'"')
            if 'encoding' not in engine:
                err.append('Missing "encoding" in database engine "'+ename+'"')

        if len(err)>0:
            err_str = "\n"
            for e in err:
                err_str += "\t\t"+e+"\n"
            raise NameError('Configuration errors in LODEL2SQLWRAPPER:'+err_str)
                

    @property
    def cfg(self):
        """ Get the dict of options for the wrapper
            Its an alias to the classes property SqlWrapper.config
            @return a dict containing the Db settings"""
        return self.__class__.config

