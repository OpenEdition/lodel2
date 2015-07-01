import os
import logging
import shutil

from django.conf import settings
from Database import sqlsetup


_TESTDB_DEFAULT_DIR = '/tmp/'
_TESTDB_DEFAULT_NAME = 'lodel2_test_db.sqlite'
_TESTDB_COPY_SUFFIX = '_bck'

## Make a copy of an empty Db created by Database::SQLSetup::initDb()
#
# Usage example :
#   #Using 'default' as dbconfname
#   def setUpModule():
#       dbname = 'supertestdb'
#       initTestDb(dbname)
#       setDbConf(dbname)
#       ...
#
#   #Using another name as dbconfname
#   def setUpModule():
#       dbname = 'superdbtest'
#       initTestDb(dbname)
#       setDbConf(dbname, 'mytest_dbconf')
#
#       db_engine = sqlutils.getEngine('mytest_dbconf')
#       EmComponent.dbconf = 'mytest_dbconf'
#       #WARNING !!! This example as few chances to work due to the bad isolation of data sources in EmComponent... Will be solved with the EM object
#
def initTestDb(dbname = _TESTDB_DEFAULT_NAME, dbdir = _TESTDB_DEFAULT_DIR):

    dbname = os.path.join(dbdir, dbname)
    db_default = os.path.join(_TESTDB_DEFAULT_DIR, _TESTDB_DEFAULT_NAME)
    db_copy = os.path.join(_TESTDB_DEFAULT_DIR, _TESTDB_DEFAULT_NAME+_TESTDB_COPY_SUFFIX)

    if not os.path.isfile(db_copy):
        #The 'backup' copy didn't exists yet. Create it.
        settings.LODEL2SQLWRAPPER['db']['dbtest_default'] = {
            'ENGINE': 'sqlite',
            'NAME': db_default,
        }
        sqlsetup.init_db(dbconfname = 'dbtest_default')
        #Make the backup copy
        shutil.copyfile(db_default, db_copy)
    
    #Copy the Db at the wanted location
    shutil.copyfile(db_copy, dbname)
    return dbname

def copyDb(dbname_src, dbname_dst, dbdir_src = _TESTDB_DEFAULT_DIR, dbdir_dst = _TESTDB_DEFAULT_DIR):
    dbname_src = os.path.join(dbdir_src, dbname_src)
    dbname_dst = os.path.join(dbdir_dst, dbname_dst)
    shutil.copyfile(dbname_src, dbname_dst)
    pass


def saveDbState(dbname = _TESTDB_DEFAULT_NAME, dbdir = _TESTDB_DEFAULT_DIR):
    dbname = os.path.join(dbdir, dbname)
    shutil.copyfile(dbname, dbname+_TESTDB_COPY_SUFFIX)
    pass

def restoreDbState(dbname = _TESTDB_DEFAULT_NAME, dbdir = _TESTDB_DEFAULT_DIR):
    dbname = os.path.join(dbdir, dbname)
    shutil.copyfile(dbname+_TESTDB_COPY_SUFFIX, dbname)
    pass

def cleanDb(dbname = _TESTDB_DEFAULT_NAME, dbdir = _TESTDB_DEFAULT_DIR):
    dbname = os.path.join(dbdir, dbname)
    try: os.unlink(dbname)
    except:pass
    try: os.unlink(dbname+_TESTDB_COPY_SUFFIX)
    except:pass
    pass


def setDbConf(dbname, dbconfname = 'default', dbdir = _TESTDB_DEFAULT_DIR):
    
    settings.LODEL2SQLWRAPPER['db'][dbconfname] = {
        'ENGINE': 'sqlite',
        'NAME': os.path.join(_TESTDB_DEFAULT_DIR, dbname)
    }
    pass
 
    
