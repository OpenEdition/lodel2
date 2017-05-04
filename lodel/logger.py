#-*- coding: utf-8 -*-

import copy
import logging, logging.handlers
import os.path

# Variables & constants definitions
default_format = '%(asctime)-15s %(levelname)s %(_pathname)s:%(_lineno)s:%(_funcName)s() : %(message)s'
simple_format = '%(asctime)-15s %(levelname)s : %(message)s'
SECURITY_LOGLEVEL = 35
logging.addLevelName(SECURITY_LOGLEVEL, 'SECURITY')
handlers = dict() # Handlers list (generated from settings)
##@brief Stores sent messages until module is able to be initialized
msg_buffer = []

# Fetching logger for current context
from lodel.context import LodelContext
logger = logging.getLogger(LodelContext.get_name())

##@brief Module initialisation from settings
#@return True if inited else False
def __init_from_settings():
    from lodel.settings import Settings
    from lodel.settings.settings import Settings, Lodel2Settings
    if not Lodel2Settings.started():
        return False
    # capture warning disabled, because the custom format raises error (unable
    # to give the _ preffixed arguments to logger resulting into a KeyError
    # exception )
    #logging.captureWarnings(True) # Log warnings

    logger.setLevel(logging.DEBUG)
    for name in Settings.logging._fields:
        add_handler(name, getattr(Settings.logging, name))
    return True
    

##@brief Add an handler, identified by a name, to a given logger 
#
# logging_opt is a dict with logger option. Allowed keys are : 
# - filename : take a filepath as value and cause the use of a logging.handlers.RotatingFileHandler
# - level : the minimum logging level for a logger, takes values [ 'DEBUG', 'INFO', 'WARNING', 'SECURITY', 'ERROR', 'CRITICAL' ]
# - format : DONT USE THIS OPTION (or if you use it be sure to includes %(_pathname)s %(_lineno)s %(_funcName)s format variables in format string
# - context : boolean, if True include the context (module:lineno:function_name) in the log format
# @todo Move the logging_opt documentation somewhere related with settings
# 
# @param name str : The handler name
# @param logging_opt dict : dict containing options ( see above )
def add_handler(name, logging_opt):
    logger = logging.getLogger(LodelContext.get_name())
    if name in handlers:
        raise KeyError("A handler named '%s' allready exists")
    
    logging_opt = logging_opt._asdict()
    if 'filename' in logging_opt and logging_opt['filename'] is not None:
        maxBytes = (1024 * 10) if 'maxbytes' not in logging_opt else logging_opt['maxbytes']
        backupCount = 10 if 'backupcount' not in logging_opt else logging_opt['backupcount']

        handler = logging.handlers.RotatingFileHandler(
                                        logging_opt['filename'],
                                        maxBytes = maxBytes,
                                        backupCount = backupCount,
                                        encoding = 'utf-8')
    else:
        handler = logging.StreamHandler()
    
    if 'level' in logging_opt:
        handler.setLevel(getattr(logging, logging_opt['level'].upper()))

    if 'format' in logging_opt:
        formatter = logging.Formatter(logging_opt['format'])
    else:
        if 'context' in logging_opt and not logging_opt['context']:
            formatter = logging.Formatter(simple_format)
        else:
            formatter = logging.Formatter(default_format)

    handler.setFormatter(formatter)
    handlers[name] = handler
    logger.addHandler(handler)
    

##@brief Remove an handler generated from configuration (runtime logger configuration)
# @param name str : handler name
def remove_handler(name):
    if name in handlers:
        logger.removeHandler(handlers[name])
    # else: can we do anything ?

##@brief Utility function that disable unconditionnaly handlers that implies console output
# @note In fact, this function disables handlers generated from settings wich are instances of logging.StreamHandler
def remove_console_handlers():
    for name, handler in handlers.items():
        if isinstance(handler, logging.StreamHandler):
            remove_handler(name)
    
#####################
# Utility functions #
#####################

##@brief Generic logging function
# @param lvl int : Log severity
# @param msg str : log message
# @param *args : additional positionnal arguments
# @param **kwargs : additional named arguments
def log(lvl, msg, *args, **kwargs):
    if len(handlers) == 0: #late initialisation
        if not __init_from_settings():
            s_kwargs = copy.copy(kwargs)
            s_kwargs.update({'lvl': lvl, 'msg':msg})
            msg_buffer.append((s_kwargs, args))
            return
        else:
            for s_kwargs, args in msg_buffer:
                log(*args, **s_kwargs)
    from lodel.context import LodelContext
    if LodelContext.multisite():
        msg = "CTX(%s) %s" % (LodelContext.get_name(), msg)
    caller = logger.findCaller() # Opti warning : small overhead
    extra = {
        '_pathname': os.path.abspath(caller[0]),
        '_lineno': caller[1],
        '_funcName': caller[2],
    }
    logger.log(lvl, msg, extra = extra, *args, **kwargs)

def debug(msg, *args, **kwargs): log(logging.DEBUG, msg, *args, **kwargs)
def info(msg, *args, **kwargs): log(logging.INFO, msg, *args, **kwargs)
def warning(msg, *args, **kwargs): log(logging.WARNING, msg, *args, **kwargs)
def security(msg, *args, **kwargs): log(SECURITY_LOGLEVEL, msg, *args, **kwargs)
def error(msg, *args, **kwargs): log(logging.ERROR, msg, *args, **kwargs)
def critical(msg, *args, **kwargs): log(logging.CRITICAL, msg, *args, **kwargs)

