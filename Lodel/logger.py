#-*- coding: utf-8 -*-

import logging, logging.handlers
import os.path
from Lodel.settings import Settings

# Variables & constants definitions
default_format = '%(asctime)-15s %(levelname)s %(_pathname)s:%(_lineno)s:%(_funcName)s() %(message)s'
SECURITY_LOGLEVEL = 35
logging.addLevelName(SECURITY_LOGLEVEL, 'SECURITY')

# Disabled, because the custom format raises error (enable to give the _ preffixed arguments to logger resulting into a KeyError exception )
#logging.captureWarnings(True) # Log warnings

# Fetching default root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Setting options from Lodel.settings.Settings.logging
for logging_opt in Settings.logging:
    print("Ben woot !")
    if 'filename' in logging_opt:
        maxBytes = (1024 * 10) if 'maxBytes' not in logging_opt else logging_opt['maxBytes']
        backupCount = 10 if 'backupCount' not in logging_opt else logging_opt['backupCount']

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
        formatter = logging.Formatter(default_format)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Utility functions

## @brief Generic logging function
# @param lvl int : Log severity
# @param msg str : log message
# @param *args : additional positionnal arguments
# @param **kwargs : additional named arguments
def log(lvl, msg, *args, **kwargs):
    caller = logger.findCaller() # Opti warning : small overhead
    extra = {
        '_pathname': os.path.relpath(caller[0]), # os.path.relpath add another small overhead
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
