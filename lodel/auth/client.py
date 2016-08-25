#-*- Coding: utf-8 -*-

import copy
import sys
import warnings

from lodel.settings import Settings
from lodel import logger
from lodel.plugin.hooks import LodelHook
from lodel.plugin import SessionHandlerPlugin as SessionHandler
from .exceptions import *

##@brief Class designed to handle sessions and its datas
class LodelSession(object):
    
    ##@brief Try to restore or to create a session
    #@param token None | mixed : If None no session will be loaded nor created
    #restore an existing session
    #@throw  ClientAuthenticationFailure if a session restore fails
    def __init__(self, token = None):
        ##@brief Stores the session token
        self.__token = token
        ##@brief Stores the session datas
        self.__datas = dict()
        if token is not None:
            self.restore(token)
    
    ##@brief A token reference checker to ensure token deletion at the end of
    #a session
    #@warning Cause maybe a performance issue !
    def __token_checker(self):
        refcount = sys.getrefcount(self.__token)
        if self.__token is not None and refcount > 1:
            warnings.warn("More than one reference to the session token \
exists ! (exactly %d)" % refcount)

    ##@brief Property. Equals True if a session is started else False
    @property
    def started(self):
        res = self.__token is not None
        if res:
            self.__token_checker()
        return res
    
    ##@brief Property that ensure ro acces to sessions datas
    @property
    def datas(self):
        return copy.copy(self.__datas)
    
    ##@brief Return the session token
    def retrieve_token(self):
        # DO NOT COPY THE TOKEN TO ENSURE THAT NOT MORE THAN ONE REFERENCE TO
        # IT EXISTS
        return self.__token

    ##@brief Late restore of a session
    #@param token mixed : the session token
    #@throw ClientAuthenticationError if a session was allready started
    #@throw ClientAuthenticationFailure if no session exists with this token
    def restore(self, token):
        if self.started:
            raise ClientAuthenticationError("Trying to restore a session, but \
a session is allready started !!!")
        self.__datas = SessionHandler.restore(token)
        self.__token = token
        return self.datas

    ##@brief Save the current session state
    def save(self):
        if not self.started:
            raise ClientAuthenticationError(
                "Trying to save a non started session")
        SessionHandler.save(self.__token, self.__datas)
    
    ##@brief Destroy a session
    def destroy(self):
        if not self.started:
            logger.debug("Destroying a session that is not started")
        else:
            SessionHandler.destroy(self.__token)
        self.__token = None
        self.__datas = dict()
    
    ##@brief Destructor
    def __del__(self):
        del(self.__token)
        del(self.__datas)

    ##@brief Implements setter for dict access to instance
    #@todo Custom exception throwing
    def __setitem__(self, key, value):
        self.__init_session() #Start the sesssion
        self.__datas[key] = value
    
    ##@brief Implements destructor for dict access to instance
    #@todo Custom exception throwing
    def __delitem__(self, key):
        if not self.started:
            raise ClientAuthenticationError(
                "Data read access to a non started session is not possible")
        del(self.__datas[key])
    
    ##@brief Implements getter for dict acces to instance
    #@todo Custom exception throwing
    def __getitem__(self, key):
        if not self.started:
            raise ClientAuthenticationError(
                "Data read access to a non started session is not possible")
        return self.__datas[key]

    ##@brief Start a new session
    #@note start a new session only if no session started yet
    def __init_session(self):
        if self.__token is not None:
            return
        self.__token = SessionHandler.start()
            
        

##@brief Client metaclass designed to implements container accessor on 
#Client Class
#
#@todo Maybe we can delete this metaclass....
class ClientMetaclass(type):
    
    def __init__(self, name, bases, attrs):
        return super(ClientMetaclass, self).__init__(name, bases, attrs)

    def __getitem__(self, key):
        return self.session()[key]

    def __delitem__(self, key):
        del(self.session()[key])

    def __setitem__(self, key, value):
        self.session()[key] = value

    def __str__(self):
        return str(self._instance)

##@brief Abstract singleton class designed to handle client informations
#
# This class is designed to handle client authentication and sessions
class Client(object, metaclass = ClientMetaclass):
    
    ##@brief Singleton instance
    _instance = None
    ##@brief List of dict that stores field ref for login and password
    #
    # Storage specs : 
    #
    # A list of dict, with keys 'login' and 'password', items are tuple.
    #- login tuple contains (LeObjectChild, FieldName, link_field) with:
    # - LeObjectChild the dynclass containing the login
    # - Fieldname the fieldname of LeObjectChild containing the login
    # - link_field None if both login and password are in the same
    # LeObjectChild. Else contains the field that make the link between
    # login LeObject and password LeObject
    #- password typle contains (LeObjectChild, FieldName)
    _infos_fields = None
    
    ##@brief Constant that stores the session key that stores authentication
    #informations
    _AUTH_DATANAME = '__auth_user_infos'
    

    ##@brief Constructor
    #@param session_token mixed : Session token provided by client to interface
    def __init__(self,session_token = None):
        if self.__class__ == Client:
            raise NotImplementedError("Abstract class")
        logger.debug("New instance of Client child class %s" %
            self.__class__.__name__)
        if Client._instance is not None:
            old = Client._instance
            Client._instance = None
            del(old)
            logger.debug("Replacing old Client instance by a new one")
        else:
            #first instanciation, fetching settings
            self.fetch_settings()
        ##@brief Stores infos for authenticated users (None == anonymous)
        self.__user = None
        ##@brief Stores the session handler
        Client._instance = self
        ##@brief Stores LodelSession instance
        self.__session = LodelSession(session_token)
        logger.debug("New client : %s" % self)
    
    def __del__(self):
        del(self.__session)

    ##@brief Try to authenticate a user with a login and a password
    #@param login str : provided login
    #@param password str : provided password (hash)
    #@warning brokes composed UID
    #@note implemets multiple login/password sources (useless ?)
    #@todo composed UID broken method
    #@todo allow to provide an authentication source
    @classmethod
    def authenticate(self, login = None, password = None):
        #Authenticate
        for infos in self._infos_fields:
            login_cls = infos['login'][0]
            pass_cls = infos['pass'][0]
            qfilter = "{passfname} = {passhash}"
            uid_fname = login_cls.uid_fieldname()[0] #COMPOSED UID BROKEN
            if login_cls == pass_cls:
                #Same EmClass for login & pass
                qfilter = qfilter.format(
                    passfname = infos['pass'][1],
                    passhash = password)
            else:
                #Different EmClass, building a relational filter
                passfname = "%s.%s" % (infos['login'][2], infos['pass'][1])
                qfilter = qfilter.format(
                    passfname = passfname,
                    passhash = password)
            getq = LeGetQuery(infos['login'][0], qfilter,
                field_list = [uid_fname], limit = 1)
            req = getq.execute()
            if len(req) == 1:
                #Authenticated
                self.__set_authenticated(infos['login'][0], req[uid_fname])
                break
        if self.is_anon():
            self.fail() #Security logging
    
    ##@brief Attempt to restore a session given a session token
    #@param token mixed : a session token
    #@return Session datas (a dict)
    #@throw ClientAuthenticationFailure if token is not valid or not
    #existing
    @classmethod
    def restore_session(cls, token):
        cls._assert_instance()
        return Client._instance.__session.restore(token)
    
    ##@brief Return the current session token or None
    #@return A session token or None
    @classmethod
    def session_token(cls):
        cls._assert_instance()
        return Client._instance.__session.retrieve_token()

    @classmethod
    def session(cls):
        cls._assert_instance()
        return Client._instance.__session
    
    ##@brief Delete current session
    @classmethod
    def destroy(cls):
        cls._assert_instance()
        Client._instance.__session.destroy()
    
    ##@brief Delete current client and save its session
    @classmethod
    def clean(cls):
        if Client._instance.__session.started:
            Client._instance.__session.save()
        if Client._instance is not None:
            del(Client._instance)
        Client._instance = None
    
    ##@brief Test wether a client is anonymous or logged in
    #@return True if client is anonymous
    @classmethod
    def is_anonymous(cls):
        cls._assert_instance()
        return Client._instance

    ##@brief Method to call on authentication failure
    #@throw ClientAuthenticationFailure
    #@throw LodelFatalError if no Client child instance found
    @classmethod
    def authentication_failure(cls):
        cls._generic_error(ClientAuthenticationFailure)
    
    ##@brief Method to call on authentication error
    #@throw ClientAuthenticationError
    #@throw LodelFatalError if no Client child instance found
    @classmethod
    def authentication_error(cls, msg = "Unknow error"):
        cls._generic_error(ClientAuthenticationError, msg)

    ##@brief Method to call on permission denied error
    #@throw ClientPermissionDenied
    #@throw LodelFatalError if no Client child instance found
    @classmethod
    def permission_denied_error(cls, msg = ""):
        cls._generic_error(ClientPermissionDenied, msg)
    
    ##@brief Generic error method
    #@see Client::authentication_failure() Client::authentication_error()
    #Client::permission_denied_error()
    #@throw LodelFatalError if no Client child instance found
    @classmethod
    def _generic_error(cls, expt, msg = ""):
        cls._assert_instance()
        raise expt(Client._instance, msg)
    
    ##@brief Assert that an instance of Client child class exists
    #@throw LodelFataError if no instance of Client child class found
    @classmethod
    def _assert_instance(cls):
        if Client._instance is None:
            raise LodelFatalError("No client instance found. Abording.")

    ##@brief Class method that fetches conf
    #
    #This method populates Client._infos_fields . This attribute stores
    #informations on login and password location (LeApi object & field)
    @classmethod
    def fetch_settings(cls):
        from lodel import dyncode
        if cls._infos_fields is None:
            cls._infos_fields = list()
        else:
            #Allready fetched
            return
        infos = (
            Settings.auth.login_classfield,
            Settings.auth.pass_classfield)
        res_infos = []
        for clsname, fieldname in infos:
            dcls = dyncode.lowername2class(infos[0][0])
            res_infos.append((dcls, infos[1][1]))

        link_field = None
        if res_infos[0][0] != res_infos[1][0]:
            # login and password are in two separated EmClass
            # determining the field that links login EmClass to password
            # EmClass
            for fname, fdh in res_infos[0][0].fields(True).items():
                if fdh.is_reference() and res_infos[1][0] in fdh.linked_classes():
                    link_field = fname
            if link_field is None:
                #Unable to find link between login & password EmClasses
                raise AuthenticationError("Unable to find a link between \
login EmClass '%s' and password EmClass '%s'. Abording..." % (
                    res_infos[0][0], res_infos[1][0]))
        res_infos[0] = (res_infos[0][0], res_infos[0][1], link_field)
        cls._infos_fields.append(
            {'login':res_infos[0], 'password':res_infos[1]})

    ##@brief Set a user as authenticated and start a new session
    #@param leo LeObject child class : the LeObject the user is stored in
    #@param uid str : uniq id (in leo)
    #@return None
    def __set_authenticated(self, leo, uid):
        self.__user = {'classname': leo.__name__, 'uid': uid, 'leoclass': leo}
        #Store auth infos in session
        self.__session[self.__class__._AUTH_DATANAME] = copy.copy(self.__user)
        
    
