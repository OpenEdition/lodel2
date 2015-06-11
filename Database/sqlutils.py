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

def meta(engine):
		res = sqla.MetaData()
		res.reflect(bind=engine)
		return res
