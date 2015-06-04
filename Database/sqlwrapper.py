# -*- coding: utf-8 -*-
import os
import re
import logging as logger

import sqlalchemy as sqla
from sqlalchemy.ext.compiler import compiles
from django.conf import settings

from Database.sqlalter import *

#Logger config
logger.getLogger().setLevel('DEBUG')
#To be able to use dango confs
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

class SqlWrapper(object):
    """ A wrapper class to sqlalchemy

        Usefull to provide a standart API

        __Note__ : This class is not thread safe (sqlAlchemy connections are not). Create a new instance of the class to use in different threads or use SqlWrapper::copy
    """
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
    
    ##Configuration dict alias for class access
    config=settings.LODEL2SQLWRAPPER
    
    ##Wrapper instance list
    wrapinstance = dict()

    def __init__(self, name=None, alchemy_logs=None, read_db = "default", write_db = "default"):
        """ Instanciate a new SqlWrapper
            @param name str: The wrapper name
            @param alchemy_logs bool: If true activate sqlalchemy logger
            @param read_db str: The name of the db conf
            @param write_db str: The name of the db conf

            @todo Better use of name (should use self.cfg['wrapper'][name] to get engines configs
            @todo Is it a really good idea to store instance in class scope ? Maybe not !!
        """
        
        self.sqlalogging = False if alchemy_logs == None else bool(alchemy_logs)

        if name == None:
            self.name = read_db+'+'+write_db
        else:
            self.name = name
    
        self.r_dbconf = read_db
        self.w_dbconf = write_db

        self.checkConf() #raise if errors in configuration

        if self.name in self.__class__.wrapinstance:
            logger.warning("A SqlWrapper with the name "+self.name+" allready exist. Replacing the old one by the new one")
        SqlWrapper.wrapinstance[self.name] = self

        #Engine and wrapper initialisation
        self.r_engine = self._getEngine(True, self.sqlalogging)
        self.w_engine = self._getEngine(False, self.sqlalogging)
        self.r_conn = None
        self.w_conn = None


        self.metadata = None #TODO : use it to load all db schema in 1 request and don't load it each table instanciation
        self.meta_crea = None

        logger.debug("New wrapper instance : <"+self.name+" read:"+str(self.r_engine)+" write:"+str(self.w_engine))
        pass

    @property
    def cfg(self): return self.__class__.config;
    @property
    def engines_cfg(self): return self.__class__.ENGINES;

    @property
    def meta(self):
        if self.metadata == None:
            self.renewMetaData()
        return self.metadata

    def renewMetaData(self):
        """ (Re)load the database schema """
        if self.metadata == None:
            self.metadata = sqla.MetaData(bind=self.r_engine, reflect=True)
        else:
            self.metadata = sqla.MetaData(bind=self.r_engine, reflect=True)

    @property
    def rconn(self):
        """ Return the read connection
            @warning Do not store the connection, call this method each time you need it
        """
        return self.getConnection(True)
    @property
    def wconn(self):
        """ Return the write connection
            @warning Do not store the connection, call this method each time you need it
        """
        return self.getConnection(False)

    def getConnection(self, read):
        """ Return an opened connection
            @param read bool: If true return the reading connection
            @return A sqlAlchemy db connection
        """
        if read:
            r = self.r_conn
        else:
            r = self.w_conn

        if r == None:
            #Connection not yet opened
            self.connect(read)
            r = self.getConnection(read) #TODO : Un truc plus safe/propre qu'un appel reccursif ?
        return r


    def connect(self, read = None):
        """ Open a connection to a database
            @param read bool|None: If None connect both, if True only connect the read side (False the write side)
            @return None
        """
        if read or read == None:
            if self.r_conn != None:
                logger.debug(' SqlWrapper("'+self.name+'") Unable to connect, already connected')
            else:
                self.r_conn = self.r_engine.connect()

        if not read or read == None:
            if self.w_conn != None:
                logger.debug(' SqlWrapper("'+self.name+'") Unable to connect, already connected')
            else:
                self.w_conn = self.w_engine.connect()

    def disconnect(self, read = None):
        """ Close a connection to a database
            @param read bool|None: If None disconnect both, if True only connect the read side (False the write side)
            @return None
        """
        if read or read == None:
            if self.r_conn == None:
                logger.info('Unable to close read connection : connection not opened')
            else:
                self.r_conn.close()
            self.r_conn = None

        if not read or read == None:
            if self.r_conn == None:
                logger.info('Unable to close write connection : connection not opened')
            else:
                self.w_conn.close()
            self.w_conn = None

    def reconnect(self, read = None):
        """ Close and reopen a connection to a database
            @param read bool|None: If None disconnect both, if True only connect the read side (False the write side)
            @return None
        """
        self.disconnect(read)
        self.connect(read)

    @classmethod
    def reconnectAll(c, read = None):
        for wname in c.wrapinstance:
            c.wrapinstance[wname].reconnect(read)
            
    def Table(self, tname):
        """ Instanciate a new SqlAlchemy Table
            @param tname str: The table name
            @return A new instance of SqlAlchemy::Table
        """
        if not isinstance(tname, str):
            return TypeError('Excepting a <class str> but got a '+str(type(tname)))
        #return sqla.Table(tname, self.meta, autoload_with=self.r_engine, autoload=True)
        return sqla.Table(tname, self.meta)

    def _getEngine(self, read=True, sqlalogging = None):
        """ Return a sqlalchemy engine
            @param read bool: If True return the read engine, else 
            return the write one
            @return a sqlachemy engine instance

            @todo Put the check on db config in SqlWrapper.checkConf()
        """
        #Loading confs
        cfg = self.cfg['db'][self.r_dbconf if read else self.w_dbconf]

        edata = self.engines_cfg[cfg['ENGINE']] #engine infos
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


        ret = sqla.create_engine(conn_str, encoding=edata['encoding'], echo=self.sqlalogging)

        logger.debug("Getting engine :"+str(ret))

        return ret

    @classmethod
    def getWrapper(c, name):
        """ Return a wrapper instance from a wrapper name
            @param name str: The wrapper name
            @return a SqlWrapper instance

            @throw KeyError
        """
        if name not in c.wrapinstance:
            raise KeyError("No wrapper named '"+name+"' exists")
        return c.wrapinstance[name]

    def checkConf(self):
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
        if 'db' not in self.cfg:
            err.append('Missing "db" in configuration')
        else:
            for dbname in [self.r_dbconf, self.w_dbconf]:
                if dbname not in self.cfg['db']:    
                    err.append('Missing "'+dbname+'" db configuration')
                else:
                    db = self.cfg['db'][dbname]
                    if 'ENGINE' not in db:
                        err.append('Missing "ENGINE" in database "'+db+'"')
                    else:
                        if db['ENGINE'] not in self.engines_cfg:
                            err.append('Unknown engine "'+db['ENGINE']+'"')
                        elif db['ENGINE'] != 'sqlite' and 'USER' not in db:
                            err.append('Missing "User" in configuration of database "'+dbname+'"')
                    if 'NAME' not in db:
                        err.append('Missing "NAME" in database "'+dbname+'"')
                        
        if len(err)>0:
            err_str = "\n"
            for e in err:
                err_str += "\t\t"+e+"\n"
            raise NameError('Configuration errors in LODEL2SQLWRAPPER:'+err_str)
    
    def dropAll(self):
        """ Drop ALL tables from the database """
        if not settings.DEBUG:
            logger.critical("Trying to drop all tables but we are not in DEBUG !!!")
            raise RuntimeError("Trying to drop all tables but we are not in DEBUG !!!")
        meta = sqla.MetaData(bind=self.w_engine, reflect = True)
        meta.drop_all()
        pass

    def createAllFromConf(self, schema):
        """ Create a bunch of tables from a schema
            @param schema list: A list of table schema
            @see SqlWrapper::createTable()
        """
        self.meta_crea = sqla.MetaData()

        logger.info("Running function createAllFromConf")
        for i,table in enumerate(schema):
            self.createTable(**table)

        self.meta_crea.create_all(bind = self.w_engine)
        logger.info("All tables created")
        self.meta_crea = None
        self.renewMetaData()
        pass
            
    def createTable(self, name, columns, **kw):
        """ Create a table
            @param name str: The table name
            @param columns list: A list of columns description dict
            @param extra dict: Extra arguments for table creation
            @see SqlWrapper::createColumn()
        """

        if self.meta_crea == None:
            self.meta_crea = sqla.MetaData()
            crea_now = True
        else:
            crea_now = False

        if not isinstance(name, str):
            raise TypeError("<class str> excepted for table name, but got "+type(name))

        res = sqla.Table(name, self.meta_crea, **kw)
        for i,col in enumerate(columns):
            res.append_column(self.createColumn(**col))

        if crea_now:
            self.meta_crea.create_all(self.w_engine)

        #logger.debug("Table '"+name+"' created")
        pass

    def createColumn(self, **kwargs):
        """ Create a Column
            
            Accepte named parameters :
                - name : The column name
                - type : see SqlWrapper::_strToSqlAType()
                - extra : a dict like { "primarykey":True, "nullable":False, "default":"test"...}
            @param **kwargs 
        """
        if not 'name' in kwargs or ('type' not in kwargs and 'type_' not in kwargs):
            pass#ERROR

        #Converting parameters
        if 'type_' not in kwargs and 'type' in kwargs:
            kwargs['type_'] = self._strToSqlAType(kwargs['type'])
            del kwargs['type']

        if 'extra' in kwargs:
            #put the extra keys in kwargs
            for exname in kwargs['extra']:
                kwargs[exname] = kwargs['extra'][exname]
            del kwargs['extra']

        if 'foreignkey' in kwargs:
            #Instanciate a fk
            fk = sqla.ForeignKey(kwargs['foreignkey'])
            del kwargs['foreignkey']
        else:
            fk = None

        if 'primarykey' in kwargs:
            #renaming primary_key in primarykey in kwargs
            kwargs['primary_key'] = kwargs['primarykey']
            del kwargs['primarykey']


        res = sqla.Column(**kwargs)

        if fk != None:
            res.append_foreign_key(fk)

        #logger.debug("Column '"+kwargs['name']+"' created")
        return res
    
    def _strToSqlAType(self, strtype):
        """ Convert a string to an sqlAlchemy column type """

        if 'VARCHAR' in strtype:
            return self._strToVarchar(strtype)
        else:
            try:
                return getattr(sqla, strtype)
            except AttributeError:
                raise NameError("Unknown type '"+strtype+"'")
        pass

    def _strToVarchar(self, vstr):
        """ Convert a string like 'VARCHAR(XX)' (with XX an integer) to a SqlAlchemy varchar type"""
        check_length = re.search(re.compile('VARCHAR\(([\d]+)\)', re.IGNORECASE), vstr)
        column_length = int(check_length.groups()[0]) if check_length else None
        return sqla.VARCHAR(length=column_length)
     
    @classmethod
    def engineFamily(c, engine):
        """ Given an engine return the db family
            @see SqlWrapper::ENGINES
            @return A str or None
        """
        for fam in c.ENGINES:
            if engine.driver == c.ENGINES[fam]['driver']:
                return fam
        return None

    @property
    def wEngineFamily(self):
        """ Return the db family of the write engine
            @return a string or None
        """
        return self.__class__.engineFamily(self.w_engine)
    @property   
    def rEngineFamily(self):
        """ Return the db family of the read engine
            @return a string or None
        """
        return self.__class__.engineFamily(self.r_engine)

    def dropColumn(self, tname, colname):
        """ Drop a column from a table
            @param tname str|sqlalchemy.Table: The table name or a Table object
            @param colname str|sqlalchemy.Column: The column name or a column object
            @return None
        """
        if tname not in self.meta.tables: #Useless ?
            raise NameError("The table '"+tname+"' dont exist")
        table = self.Table(tname)
        col = sqla.Column(colname)

        ddl = DropColumn(table, col)
        sql = ddl.compile(dialect=self.w_engine.dialect)
        sql = str(sql)
        logger.debug("Executing SQL  : '"+sql+"'")
        ret = bool(self.w_engine.execute(sql))

        self.renewMetaData()
        return ret

    
    def addColumn(self, tname, colname, coltype):
        """ Add a column to a table
            @param tname str: The table name
            @param colname str: The column name
            @param coltype str: The new column type

            @return True if query success False if it fails
        """
        newcol = self.createColumn(name=colname, type_ = coltype)
        if tname not in self.meta.tables: #Useless ?
            raise NameError("The table '"+tname+"' dont exist")
        table = self.Table(tname)

        ddl = AddColumn(table, newcol)
        sql = ddl.compile(dialect=self.w_engine.dialect)
        sql = str(sql)
        logger.debug("Executing SQL  : '"+sql+"'")
        ret = bool(self.wconn.execute(sql))

        self.renewMetaData()
        return ret

    def alterColumn(self, tname, colname, col_newtype):
        """ Change the type of a column
            @param tname str: The table name
            @param colname str: The column name
            @param col_newtype str: The column new type

            @return True if query successs False if it fails
        """
        
        if self.wEngineFamily == 'sqlite':
            raise NotImplementedError('AlterColumn not yet implemented for sqlite engines')
            

        col = self.createColumn(name=colname, type_=col_newtype)
        table = self.Table(tname)

        typepref = 'TYPE ' if self.wEngineFamily == 'postgresql' else ''

        query = 'ALTER TABLE %s ALTER COLUMN %s %s'%(table.name, col.name, typepref+col.type)

        logger.debug("Executing SQL : '"+query+"'")

        ret = bool(self.wconn.execute(query))

        self.renewMetaData()
        return ret

    def _debug__printSchema(self):
        """ Debug function to print the db schema """
        print(self.meta)
        for tname in self.meta.tables:
            self._debug__printTable(tname)

    def _debug__printTable(self, tname):
        t = self.meta.tables[tname]
        tstr = 'Table : "'+tname+'" :\n'
        for c in t.c:
            tstr += '\t\t"'+c.name+'"('+str(c.type)+') \n'
        print(tstr)
            

