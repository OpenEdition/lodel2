#-*- coding: utf-8 -*-

from lodel.settings import Settings
from lodel import logger
from lodel.plugin.hooks import LodelHook
from lodel.leapi.query import LeGetQuery
from lodel.exceptions import *
from .exceptions import *

##@brief Abstract class designed to be implemented by plugin interfaces
#
#A singleton class storing current client informations.
#
#For the moment the main goal is to be able to produce security log
#containing well formated client informations
class Client(object):

    ##@brief Stores the singleton instance
    _instance = None
    
    ##@brief Implements singleton behavior
    def __init__(self):
        if self.__class__ == Client:
            raise NotImplementedError("Abstract class")
        logger.debug("New instance of %s" % self.__class__.__name__)
        if self._instance is not None:
            old = self._instance
            self._instance = None
            del(old)
            logger.debug("Replacing old Client instance by a new one")
        Client._instance = self
        logger.debug("New client : %s" % self)

        # Instanciation done. Triggering Auth instanciation
        self.__auth = Auth(self)
    
    ##@brief Destructor
    #@note calls Auth destructor too
    def __del__(self):
        del(self.__auth)

    ##@brief Abstract method.
    #
    #@note Used to generate security log message. Avoid \n etc.
    def __str__(self):
        raise NotImplementedError("Abstract method")

    #
    #   Utility methods (Wrapper for Auth)
    #
    
    ##@brief Return current instance or raise an Exception
    #@throw AuthenticationError
    @classmethod
    def client(cls):
        if cls._instance is None:
            raise LodelFatalError("Calling a Client classmethod but no Client \
instance exists")
        return cls._instance
    
    ##@brief Alias of Client::destroy()
    @classmethod
    def deauth(cls):
        cls.destroy()
    
    ##@brief Destroy current client
    @classmethod
    def destroy(cls):
        inst = cls._instance
        cls._instance = None
        del(inst)

    ##@brief Authenticate using login an password
    #@note Wrapper on Auth.auth()
    #@param login str
    #@param password str
    #@return None
    #@throw AuthenticationFailure
    #@see Auth.auth()
    @classmethod
    def auth_password(cls, login, password):
        cls.client.auth(login, password)
        
    ##@brief Authenticate using session token
    #@param token str : session token
    #@throw AuthenticationFailure
    #@see Auth.auth_session()
    @classmethod
    def auth_session(cls, token):
        cls.client.auth_session(token)
    
    ##@brief Generic authentication method
    #
    #Possible arguments are : 
    # - authenticate(token) ( see @ref Client.auth_session() )
    # - authenticate(login, password) ( see @ref Client.auth_password() )
    #@param *args
    #@param **kwargs
    @classmethod
    def authenticate(cls, *args, **kwargs):
        token = None
        login_pass = None
        if 'token' in kwargs:
            #auth session
            if len(args) != 0 or len(kwargs) != 0:
                # security issue ?
                raise AuthenticationSecurityError(cls.client())
            else:
                session = kwargs['token']
        elif len(args) == 1:
            if len(kwargs) == 0:
                #Auth session
                token = args[0]
            elif len(kwargs) == 1:
                if 'login' in kwargs:
                    login_pass = (kwargs['login'], args[0])
                elif 'password' in kwargs:
                    login_pass = (args[0], kwargs['password'])
        elif len(args) == 2:
            login_pass = tuple(args)
        
        if login_pass is None and token is None:
            # bad arguments given. Security issue ?
            raise AuthenticationSecurityError(cls.client())
        elif login_pass is None:
            cls.auth_session(token)
        else:
            cls.auth_password(*login_pass)
        

##@brief Singleton class that handles authentication on lodel2 instances
#
#
#@note Designed to be never called directly. The Client class is designed to
#be implemented by UI and to provide a friendly/secure API for \
#client/auth/session handling
#@todo specs of client infos given as argument on authentication methods
class Auth(object):
    
    ##@brief Stores singleton instance
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
    
    ##@brief Constructor
    #
    #@note Automatic clean of previous instance
    def __init__(self, client):
        ##@brief Stores infos about logged in user
        #
        #Tuple containing (LeObjectChild, UID) of logged in user
        self.__user_infos = False
        ##@brief Stores session id
        self.__session_id = False
        if not isinstance(client, Client):
            msg = "<class Client> instance was expected but got %s"
            msg %= type(client)
            raise TypeError(msg)
        ##@brief Stores client infos
        self.__client = client
        
        # Singleton
        if self._instance is not None:
            bck = self._instance
            bck.destroy()
            self._instance = None
            logger.debug("Previous Auth instance replaced by a new one")
        else:
            #First instance, fetching settings
            self.fetch_settings()
        self.__class__._instance = self
    
    ##@brief Destroy current instance an associated session
    def _destroy(self):
        self.__user_infos = LodelHook.call_hook('lodel2_session_destroy',
            caller = self, payload = self.__session_id)
    
    ##@brief Destroy singleton instance
    @classmethod
    def destroy(cls):
        cls._instance._destroy()

    ##@brief Raise exception because of authentication failure
    #@note trigger a security log containing client infos
    #@throw LodelFatalError if no instance exsists
    #@see Auth.fail()
    @classmethod
    def failure(cls):
        if cls._instance is None:
            raise LodelFatalError("No Auth instance found. Abording")
        raise AuthenticationFailure(cls._instance.fail())

    ##@brief Class method that fetches conf
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
<<<<<<< HEAD
            res_infos.append((
                dyncode.lowername2class(infos[0]),
                dcls.field(infos[1])))  # TODO cls.field ?
=======
            dcls = dyncode.lowername2class(infos[0][0])
            res_infos.append((dcls, infos[1][1]))
>>>>>>> Plug webui to auth

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

    ##@brief Raise an AuthenticationFailure exception
    #
    #@note Trigger a security log message containing client infos
    def fail(self):
        raise AuthenticationFailure(self.__client)

    ##@brief Is the user anonymous ?
    #@return True if no one is logged in
    def is_anon(self):
        return self._login is False
    
    ##@brief Authenticate using a login and a password
    #@param login str : provided login
    #@param password str : provided password
    #@todo automatic hashing
    #@warning brokes multiple UID
    #@note implements multiple login/password sources (useless ?)
    #@todo composed UID broken in this method
    def auth(self, login = None, password = None):
        # Authenticate
        for infos in self._infos_fields:
            login_cls = infos['login'][0]
            pass_cls = infos['pass'][0]
            qfilter = "passfname = passhash"
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

    ##@brief Authenticate using a session token
    #@note Call a dedicated hook in order to allow session implementation as
    #plugin
    #@thrown AuthenticationFailure
    def auth_session(self, token):
        try:
            self.__user_infos = LodelHook.call_hook('lodel2_session_load',
                caller = self, payload = token)
        except AuthenticationError:
            self.fail() #Security logging
        self.__session_id = token
    
    ##@brief Set a user as authenticated and start a new session
    #@param leo LeObject child class : The EmClass the user belong to
    #@param uid str : uniq ID (in leo)
    #@return None
    def __set_authenticated(self, leo, uid):
        # Storing user infos
        self.__user_infos = {'classname': leo.__name__, 'uid': uid}
        # Init session
        sid = LodelHook.call_hook('lodel2_session_start', caller = self,
            payload = copy.copy(self.__user_infos))
        self.__session_id = sid

