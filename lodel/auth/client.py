#-*- Coding: utf-8 -*-

import copy
import sys
import warnings
import inspect

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings': 'Settings',
    'lodel.logger': 'logger',
    'lodel.plugin': [('SessionHandlerPlugin', 'SessionHandler')],
    'lodel.auth.exceptions': ['ClientError', 'ClientAuthenticationFailure',
        'ClientPermissionDenied', 'ClientAuthenticationError'],
    'lodel.leapi.query': ['LeGetQuery'],})

##@brief Client metaclass designed to implements container accessor on 
#Client Class
#
#@todo Maybe we can delete this metaclass....
class ClientMetaclass(type):
    
    def __init__(self, name, bases, attrs):
        return super(ClientMetaclass, self).__init__(name, bases, attrs)

    def __getitem__(self, key):
        return self.datas()[key]

    def __delitem__(self, key):
        del(self.datas()[key])

    def __setitem__(self, key, value):
        if self.get_session_token() is None:
            self.set_session_token(SessionHandler.start())
        datas = self.datas()
        datas[key] = value

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
        logger.debug(session_token)
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
        
        self.__datas = dict()
        if session_token is not None:
            self.__datas = SessionHandler.restore(session_token)
        self.__session_token = session_token
        
        logger.debug("New client : %s" % self)
    
    def __del__(self):
        del(self.__session_token)
        del(self.__datas)

    @classmethod
    def datas(cls):
        return cls._instance.__datas
    
    @classmethod
    def user(cls):
        if '__auth_user_infos' in cls._instance.__datas:
            return cls._instance.__datas['__auth_user_infos']
        else:
            return None
    @classmethod
    def get_session_token(cls):
        return cls._instance.__session_token
    
    @classmethod
    def set_session_token(cls, value):
        cls._instance.__session_token = value
    
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
            logger.debug(self._infos_fields)
            login_cls = infos['login'][0]
            pass_cls = infos['password'][0]
            qfilter = "{passfname} = {passhash}"
            uid_fname = login_cls.uid_fieldname()[0] #COMPOSED UID BROKEN
            if login_cls == pass_cls:
                #Same EmClass for login & pass
                qfilter = qfilter.format(
                    passfname = infos['password'][1],
                    passhash = password)
            else:
                #Different EmClass, building a relational filter
                passfname = "%s.%s" % (infos['login'][2], infos['password'][1])
                qfilter = qfilter.format(
                    passfname = passfname,
                    passhash = password)
            getq = LeGetQuery(infos['login'][0], qfilter,
                field_list = [uid_fname], limit = 1)
            req = getq.execute()
            if len(req) == 1:
                self.__set_authenticated(infos['login'][0],req[0][uid_fname])
                break
        if self.is_anonymous():
            self.authentication_failure() #Security logging
    
    ##@brief Attempt to restore a session given a session token
    #@param token mixed : a session token
    #@return Session datas (a dict)
    #@throw ClientAuthenticationFailure if token is not valid or not
    #existing
    @classmethod
    def restore_session(cls, token):
        cls._assert_instance()
        if cls._instance.__session_token is not None:
            raise ClientAuthenticationError("Trying to restore a session, but \
a session is allready started !!!")
        try:
            cls._instance.__datas = SessionHandler.restore(token)
            cls._instance.__session_token = token
        except ClientAuthenticationFailure:
            logger.warning("Session restoring fails")
        return copy.copy(cls._instance.datas)
    
    ##@brief Return the current session token or None
    #@return A session token or None
    @classmethod
    def session_token(cls):
        cls._assert_instance()
        return cls._instance.__session_token

   
    ##@brief Delete current session
    @classmethod
    def destroy(cls):
        cls._assert_instance()
        SessionHandler.destroy(cls._instance.__session_token)
        cls._instance.__session_token = None
        cls._instance.__datas = dict()
    
    ##@brief Delete current client and save its session
    @classmethod
    def clean(cls):
        if cls._instance.__session_token is not None:
            SessionHandler.save(cls._instance.__session_token, cls._instance.__datas)
        if Client._instance is not None:
            del(Client._instance)
        Client._instance = None
    
    ##@brief Test wether a client is anonymous or logged in
    #@return True if client is anonymous
    @classmethod
    def is_anonymous(cls):
        return Client._instance.user() is None
        
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
    @classmethod
    def __set_authenticated(cls, leo, uid):
        cls._instance.__user = {'classname': leo.__name__, 'uid': uid, 'leoclass': leo}
        #Store auth infos in session
        cls._instance.__datas[cls._instance.__class__._AUTH_DATANAME] = copy.copy(cls._instance.__user)

