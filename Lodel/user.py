#-*- coding: utf-8 -*-

## @package Lodel.user Defines classes designed to handler users and user's context
#
# Classes defined in this package are "helpers" for Lodel2 UI

import warnings
import copy
from Lodel.settings import Settings

## @brief Represent a Lodel user identity
#
# Class that produce immutable instance representing an identity
class UserIdentity(object):
    
    ## Maintain a reference to a UserIdentity instance that represents an anonymous user
    __anonymous_user = None

    ## @brief Constructor
    # @note produce immutable instance
    # @param user_id * : user id
    # @param username str : user name
    # @param fullname str | None : user full name
    # @param identified bool : set it to True if the user is identified
    # @param authenticated bool : set it to True if the user is authenticated (force identified = True )
    def __init__(self, user_id, username, fullname = None, identified = False, authenticated = False):
        self.__user_id = user_id
        self.__username = username
        self.__fullname = fullname if fullname is not None else username
        self.__authenticated = bool(authenticated)
        self.__identified = bool(identified) or self.__authenticated
    
    ## @brief getter for user id
    @property
    def user_id(self):
        return self.__user_id
    
    ## @brief getter for username
    @property
    def username(self):
        return self.__username
    
    ## @brief getter for fullname
    @property
    def fullname(self):
        return self.__fullname
    
    ## @return True if the user is considered as authenticated
    @property
    def is_authenticated(self):
        return self.__authenticated

    ## @return True if the user is considered as identified
    @property
    def is_identified(self):
        return self.__identified
    
    ## @brief String representation of the instance
    def __repr__(self):
        return "User '{user_id}'( username = '{username}', fullname = '{fullname}', identified : {identified}, authentified : {auth}".format(
                                    user_id = self.__user_id,
                                    username = self.__username,
                                    fullname = self.__fullname,
                                    identified = str(self.__identified),
                                    auth = str(self.__authenticated),
        )
    
    ## @brief Human readable text representation of the instance
    def __str__(self):
        return self.__fullname

    ## @brief Provide an instance of UserIdentity representing an anonymous user
    @classmethod
    def anonymous(cls):
        if cls.__anonymous_user is None:
            cls.__anonymous_user = UserIdentity(False, "anonymous", "Anonymous user")
        return cls.__anonymous_user


## @brief Decorator class designed to register user authentication methods
#
# @note Decorated functions are expected to take 2 arguments :
#  - identifier : the user identifier
#  - proof : a proof of identity
# and are expected to return False if authentication fails. When authentication
# is a success the function is expected to return a UserIdentity instance
class authentication_method(object):
    
    ## @brief Stores registered authentication functions
    __methods = set()
    
    ## @brief Constructor
    # @param method function : decorated function
    def __init__(self, method):
        ## @brief Decorated functions
        self._method = method
        self.__methods |= set([method]) # method registration

    ## @brief Callback called when decorated function is called
    # @return bool
    def __call__(self, identifier, proof):
        return self._method(identifier, proof)
    
    ## @brief Try to authenticate a user with registered functions
    # @param identifier * : user id
    # @param proof * : user authentication proof
    # @param cls
    # @return False or a User Identity instance
    @classmethod
    def authenticate(cls, identifier, proof):
        if len(cls.__methods) == 0:
            raise RuntimeError("No authentication method registered")
        res = False
        for method in cls.__methods:
            ret = method(identifier, proof)
            if ret is not False:
                if Settings.debug:
                    if not isinstance(ret, UserIdentity):
                        raise ValueError("Authentication method returns something that is not False nor a UserIdentity instance")
                    if res is not False:
                        warnings.warn("Multiple authentication methods returns a UserIdentity for given idetifier and proof")
                else:
                    return ret
                res = ret
        return res

    ## @return registered identification methods
    # @param cls
    @classmethod
    def list_methods(cls):
        return list(copy.copy(cls.__methods))

    ## @brief Unregister all authentication methods
    # @param cls
    # @warning REALLY NOT a good idead !
    # @note implemented for testing purpose
    @classmethod
    def __reset__(cls):
        cls.__methods = set()


## @brief Decorator class designed to register identification methods
#
# @note The decorated functions are expected to take one argument :
# - client_infos : datas for identification
# and are expected to return False if identification fails. When identification is a success
# the function is expected to return a UserIdentity instance
class identification_method(object):
    
    ## @brief Stores registered identification functions
    __methods = set()

    ## @brief decorator constructor
    # @param method function : decorated function
    def __init__(self, method):
        ## @brief Decorated functions
        self.__method = method
        self.__methods |= set([method])

    ## @brief Called when decorated function is called
    def __call__(self, client_infos):
        return self._method(client_infos)

    ## @brief Identify someone given datas
    # @param client_infos * :  datas that may identify a user
    # @param cls
    # @return False if identification fails, else returns an UserIdentity instance
    @classmethod
    def identify(cls, client_infos):
        if len(cls.__methods) == 0:
            warnings.warn("No identification methods registered")
        res = False
        for method in cls.__methods:
            ret = method(client_infos)
            if ret is not False:
                if Settings.debug:
                    if not isinstance(ret, UserIdentity):
                        raise ValueError("Identification method returns something that is not False nor a UserIdentity instance")
                    if res is not False:
                        warnings.warn("Identifying methods returns multiple identity given client_infos")
                    else:
                        res = ret
                else:
                    return ret
        return res
    
    ## @return registered identification methods
    # @param cls
    @classmethod
    def list_methods(cls):
        return list(copy.copy(cls.__methods))

    ## @brief Unregister all identification methods
    # @param cls
    # @warning REALLY NOT a good idead !
    # @note implemented for testing purpose
    @classmethod
    def __reset__(cls):
        cls.__methods = set()


## @brief Static class designed to handle user context
class UserContext(object):

    ## @brief Client infos given by user interface
    __client_infos = None
    ## @brief Stores a UserIdentity instance
    __identity = None
    ## @brief Blob of datas stored by user interface
    __context = None


    ## @brief Not callable, static class
    # @throw NotImplementedError
    def __init__(self):
        raise NotImplementedError("Static class")

    ## @brief User context constructor
    # @param client_infos * : datas for client identification (typically IP address)
    # @param **kwargs dict : context
    # @param cls
    # @todo find another exception to raise
    @classmethod
    def init(cls, client_infos, **kwargs):
        if cls.initialized():
            raise RuntimeError("Context allready initialised")
        if client_infos is None:
            raise ValueError("Argument clien_infos cannot be None")
        cls.__client_infos = client_infos
        cls.__context = kwargs
        cls.__identity = False
    
    ## @brief Identity getter (lazy identification implementation)
    # @param cls
    # @return a UserIdentity instance
    @classmethod
    def identity(cls):
        cls.assert_init()
        if cls.__identity is False:
            ret = identification_method.identify(cls.__client_infos)
            cls.__identity = UserIdentity.anonymous() if ret is False else ret
        return cls.__identity

    ## @brief authenticate a user
    # @param identifier * : user identifier
    # @param proof * : proof of identity
    # @param cls
    # @throw an exception if fails
    # @todo find a better exception to raise when auth fails
    @classmethod
    def authenticate(cls, identifier, proof):
        cls.assert_init()
        ret = authentication_method.authenticate(identifier, proof)
        if ret is False:
            raise RuntimeError("Authentication failure")
        cls.__identity = ret
    
    ## @return UserIdentity instance
    # @todo useless alias to identity()
    @classmethod
    def user_identity(cls):
        cls.assert_init()
        return cls.identity()
    
    ## @return True if UserContext is initialized
    @classmethod
    def initialized(cls):
        return cls.__client_infos is not None
    
    ## @brief Assert that UserContext is initialized
    @classmethod
    def assert_init(cls):
        assert cls.initialized(), "User context is not initialized"
    
    ## @brief Reset the UserContext
    # @warning Most of the time IT IS NOT A GOOD IDEAD
    # @note implemented for test purpose
    @classmethod
    def __reset__(cls):
        cls.__client_infos = None
        cls.__identity = None
        cls.__context = None
