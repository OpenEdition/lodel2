##@brief This module contains usefull function to handle lodelsites on FS

import os
import os.path
import shutil

from lodel.context import LodelContext
from lodel import buildconf #No need to protect it in Contexts

LodelContext.expose_module(globals(), {
    'lodel.plugin.datasource_plugin': ['AbstractDatasource', 'DatasourcePlugin'],
    'lodel.exceptions': ['LodelFatalError'],
    'lodel.settings': 'Settings'})

from .exceptions import *

LODELSITE_DATAS_PATH = os.path.join(buildconf.LODEL2VARDIR,'sites_datas')
LODELSITE_CONTEXTS_PATH = os.path.join(
    buildconf.LODEL2VARDIRE, '.sites_contexts')

##@brief Define directories architecture
#
#@note useless because a lot of those stuff would be hardcoded
LODELSITE_INSTALL_MODEL = {
    'datas' : ['uploads', 'conf.d'], #For datadir
    'ctx': ['lodel_pkg'] #for context dir
}

CONF_MODELS = os.path.join(os.path.dirname(__file__),'model_conf.d/')
CONF_AUTOCONF_FILENAME = 'lodelsites_autoconfig.ini'

##@brief Util function that returns both datadir and contextdir paths
#@param name str : the site shortname
#@return a tuple (datadir, contextdir)
def name2paths(name):
    return (os.path.join(LODELSITE_DATAS_PATH, name),
        os.path.join(LODELSITE_CONTEXTS_PATH, name))

##@brief Util function that indicate if a site exists or not
#
#This function only checks that both paths returned by name2path are
#existing directories
#@param name str : site shortname
#@return a bool
#@throws LodelSiteDatasourceInconsistency if inconsistency detected on FS
def site_exists(name):
    paths = name2paths(name)
    for path in paths:
        if os.path.is_file(path):
            msg = 'Will trying to determine if a lodesite "%s" exists we \
found that "%s" is a file, but a directory was expected' % (name, path)
            raise LodelSiteDatasourceInconsistency(msg)

    res = [False, False]
    res = [os.is_dir(paths[0]),
        os.is_dir(paths[1])]
    if res[0] != res[1]:
        msg = 'Inconsistency detected on filesystem will trying to determine \
wether a lodelsite exists or not : '
        if res[0]:
            msg += 'datadir was found but no contextdir'
        else:
            msg += 'contextdir found but no datadir'
        raise LodelSiteDatasourceInconsistency(msg)
    return res[0]

##@brief Create sites directory on filesystem
#@param name str : site shortname
#@return None
#@throws LodelSiteDatasourceError if something fails
#@throws LodelSiteDatasourceError if the site allready exists
#@todo make uploads directory name configurable
def site_directories_creation(name):
    if site_exists(name):
        raise LodelSiteDatasourceError('This site identified by "%s" \
allready exists' % name)

    data_path, ctx_path = name2paths(name)
    #Starting by creating both directories
    #Datadir
    try:
        os.mkdir(data_path)
    except FileExistsError:
        logger.fatal('This should never append ! We just checked that this \
directory do not exists. BAILOUT !')
        raise LodelFatalError('Unable to create data directory for lodelsite \
"%s", file exists')
    except Exception as e:
        raise LodelFataError(('Unable to create data directory for lodelsite \
"%s" : ' % name) + e)
    #Context dir
    try:
        os.mkdir(ctx_path)
    except FileExistsErrpr:
        logger.fatal('This should never append ! We just checked that this \
directory do not exists. BAILOUT !')
        raise LodelFatalError('Unable to create context directory for \
lodelsite "%s", file exists')
    except Exception as e:
        raise LodelFataError(('Unable to create context directory for \
lodelsite "%s" : ' % name) + e)
    
    #Child directories
    for mname, ccd in (('datas', data_path), ('ctx', ctx_path)):
        ccd = data_path
        for d in LODELSITE_INSTALL_MODEL[mname]:
            to_create = os.path.join(ccd, d)
            try:
                os.mkdir(to_create)
            except FileExistsError:
                logger.fatal('This should never append ! We just created parent \
directory. BAILOUT !')
            except Exception as e:
                raise LodelFatalError(('Unable to create %s directory for \
lodelsite "%s" : ' % (d,name)) + e)
    
##@brief Generate conffile containing informations set by lodelsites EM
#
#@param sitename str : site shortname
#@param em_groups list : list of str -> selected em_groups
#@param extensions list : list of str -> activated extensions
#@return config file content
def generate_conf(sitename, groups, extensions):
    tpl = """
[lodel2]
sitename = {sitename}
extensions = {extensions}

[lodel2.editorialmodel]
groups = {em_groups}
"""
    return tpl.format(
        sitename = sitename,
        extensions = ', '.join(extensions),
        em_groups = ', '.join(groups))

##@brief Delete generated conf and generate a new one
#@param sitename str : site shortname
#@param em_groups list : list of str -> selected em_groups
#@param extensions list : list of str -> activated extensions
#@return None
def update_conf(sitename, groups, extensions):
    data_path, _ = name2path(sitename)
    conf_dir = os.path.join(data_path, 'conf.d') #Booo hardcoded
    autoconf = os.path.join(conf_dir, CONF_AUTOCONF_FILENAME)
    try:
        os.unlink(autoconf)
    except Exception as e:
        #Dropping error on deletion
        logger.warning('Unable to delete generated conf %s when trying to \
update it %s' % (autoconf, e))
    with open(autoconf, 'w+') as cfp:
        cfp.write(generate_conf(sitename, groups, extensions))
    logger.info('Generated configuration file update for %s' % sitename)

##@brief Copy conffile from model and generate a conffile from given infos
#@param sitename str : site shortname
#@param em_groups list : list of str -> selected em_groups
#@param extensions list : list of str -> activated extensions
#@return None
def make_confs(sitename, groups, extensions):
    data_path, _ = name2path(sitename)
    conf_dir = os.path.join(data_path, 'conf.d') #Booo hardcoded
    #Config copy & forge
    for conffile in os.listdir(CONF_MODELS):
        if conffile.endswith('.ini'):
            conffile = os.path.join(CONF_MODELS, conffile)
            target_conffile = os.path.join(conf_dir, conffile)
            logger.info(
                "Copying conffile %s -> %s" % (conffile, target_conffile))
            shutil.copyfile(conffile, target_conffile)
    #Creating generated conf
    autoconf = os.path.join(conf_dir, CONF_AUTOCONF_FILENAME)
    with open(autoconf, 'w+') as cfp:
        cfp.write(generate_conf(sitename, groups, extensions))
    logger.info("Configuration file %s generated" % (autoconf))

##@brief Delete all files related to a site
#@warning can lead to dirty bugs if the site is running...
def purge(sitename):
    for todel in name2paths:
        try:
            shutil.rmtree(todel)
        except Exception as e:
            logger.error('Unable to delete "%s" folder' % todel)
    logger.info('"%s" files are deleted' % sitename)
