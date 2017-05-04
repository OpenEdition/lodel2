# -*- coding: utf-8 -*-

## @package lodel.plugins.filesystem_session.main Main entry point of the plugin

import binascii
import datetime
import os
import pickle
import re
import time
from .filesystem_session import FileSystemSession

from lodel.logger import logger
from lodel.auth.exceptions import ClientAuthenticationFailure,
from lodel.settings import Settings

__sessions = dict()

SESSION_TOKENSIZE = 150


##
# @brief generates a new session token
#
# @return str
#
# @warning The tokensize should absolutely be used as set! os.urandom function
#            takes a number of bytes as a parameter, dividing it by 2 is an
#            extremely dangerous idea as it drastically decrease the token expected 
#            entropy expected from the value set in configs.
# @remarks There is no valid reason for checking the generated token uniqueness:
#        - checking for uniqueness is slow ;
#        - keeping a dict with a few thousand keys of hundred bytes also is
#            memory expensive ;
#        - should the system get distributed while sharing session storage, there
#            would be no reasonable way to efficiently check for uniqueness ;
#        - sessions do have a really short life span, drastically reducing
#            even more an already close to inexistent risk of collision. A 64 bits
#            id would perfectly do the job, or to be really cautious, a 128 bits
#            one (actual size of UUIDs) ;
#        - if we are still willing to ensure uniqueness, then simply salt it
#            with a counter, or a timestamp, and hash the whole thing with a 
#            cryptographically secured method such as sha-2 if we are paranoids
#            and trying to avoid what will never happen, ever ;
#        - sure, two hexadecimal characters is one byte long. Simply go for 
#            bit length, not chars length.
def generate_token():
    token = binascii.hexlify(os.urandom(SESSION_TOKENSIZE//2))
    if token in __sessions.keys():
        token = generate_token()
    return token.decode('utf-8')


##
# @brief checks the validity of a given session token
#
# @param token str
# @raise ClientAuthenticationFailure for invalid or not found session token
#
# @remarks It is useless to check the token size, unless urandom you don't
#            trust in PRNG such as urandom.
# @remarks Linear key search...
# @remarks Consider renaming. The "validity of a session token" usually means
#            that it is a active session token and/or that it was actually
#            produced by the application (signed for exemple).
def check_token(token):
    if len(token) != SESSION_TOKENSIZE:
        raise ClientAuthenticationFailure("Invalid token string")
    if token not in __sessions.keys():
        raise ClientAuthenticationFailure("No session found for this token")


## @brief returns a session file path for a specific token
# @param token str
# @return str
def generate_file_path(token):
    return os.path.abspath(os.path.join(Settings.sessions.directory, Settings.sessions.file_template) % token)


##
# @brief Retrieve the token from the file system
#
# @param filepath str
# @return str|None : returns the token or None if no token was found
#
# @remarks What is the purpose of the regex right here? There should be a way
#            to avoid slow operations.
def get_token_from_filepath(filepath):
    token_regex = re.compile(os.path.abspath(os.path.join(Settings.sessions.directory, Settings.sessions.file_template % '(?P<token>.*)')))
    token_search_result = token_regex.match(filepath)
    if token_search_result is not None:
        return token_search_result.groupdict()['token']
    return None


##
# @brief Returns the session's last modification timestamp
#
# @param token str
# @return float
# @raise ValueError if the given token doesn't match with an existing session
#
# @remarks Consider renaming
# @warning Linear search in array, again. See @ref generate_token().
def get_session_last_modified(token):
    if token in __sessions[token]:
        return os.stat(__sessions[token]).st_mtime
    else:
        raise ValueError("The given token %s doesn't match with an existing session")


##
# @brief Starts a new session and returns a new token
#
# @return str : the new token
def start_session():
    session = FileSystemSession(generate_token())
    session.path = generate_file_path(session.token)
    
    with open(session.path, 'wb') as session_file:
        pickle.dump(session, session_file)

    __sessions[session.token] = session.path
    logger.debug("New session created")

    return session.token


##
# @brief destroys a session given its token
#
# @param token str
def destroy_session(token):
    check_token(token)
    if os.path.isfile(__sessions[token]):
        os.unlink(__sessions[token])
        logger.debug("Session file for %s destroyed" % token)
    del(__sessions[token])
    logger.debug("Session %s unregistered" % token)


##
# @brief Restores a session's content
#
# @param token str
# @return FileSystemSession|None
def restore_session(token):
    gc()
    check_token(token)
    logger.debug("Restoring session : %s" % token)
    if os.path.isfile(__sessions[token]):
        with open(__sessions[token], 'rb') as session_file:
            session = pickle.load(session_file)
        return session
    else:
        return None  # raise FileNotFoundError("Session file not found for the token %s" % token)


## @brief saves the session's content to a file
# @param token str
# @param datas dict
def save_session(token, datas):
    session = datas
    if not isinstance(datas, FileSystemSession):
        session = FileSystemSession(token)
        session.path = generate_file_path(token)
        session.update(datas)

    with open(__sessions[token], 'wb') as session_file:
        pickle.dump(session, session_file)

    if token not in __sessions.keys():
        __sessions[token] = session.path

    logger.debug("Session %s saved" % token)


## @brief session store's garbage collector
#
# @remarks 
def gc():
    # Unregistered files in the session directory
    session_files_directory = os.path.abspath(Settings.sessions.directory)
    for session_file in [file_path for file_path in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_path))]:
        session_file_path = os.path.join(session_files_directory, session_file)
        token = get_token_from_filepath(session_file_path)
        if token is None or token not in __sessions.keys():
            os.unlink(session_file_path)
            logger.debug("Unregistered session file %s has been deleted" % session_file)

    # Expired registered sessions
    for token in __sessions.keys():
        if os.path.isfile(__sessions[token]):
            now_timestamp = time.mktime(datetime.datetime.now().timetuple())
            if now_timestamp - get_session_last_modified(token) > Settings.sessions.expiration:
                destroy_session(token)
                logger.debug("Expired session %s has been destroyed" % token)


##
# @param token str
# @param key str
# @param value
def set_session_value(token, key, value):
    session = restore_session(token)
    session[key] = value
    save_session(token, session)

##
# @param token str
# @param key str
def get_session_value(token, key):
    session = restore_session(token)
    return session[key]

##
# @brief deletes a session value
#
# @param token str
# @param key str
#
# @todo Should we add a save_session at the end of this method?
def del_session_value(token, key):
    session = restore_session(token)
    if key in session:
        del(session[key])
