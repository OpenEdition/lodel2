#-*- coding: utf-8 -*-

import warnings
from Lodel.settings import Settings

## @brief Represent a Lodel user identity
#
# Class that produce immutable instance representing an identity
class UserIdentity(object):
    
    ## @brief Constructor
    # @note produce immutable instance
    # @param user_id * : user id
    # @param username str : printable name for user identity
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

    @property
    def is_authenticated(self):
        return self.__authenticated

    @property
    def is_identified(self):
        return self.__identified
    
    ## @brief getter for fullname
    @property
    def fullname(self):
        return self.__fullname

    def __repr__(self):
        return "%s(id=%s)" % (self.__username, self.__user_id)

    def __str__(self):
        return self.__fullname

anonymous_user = UserIdentity(False, "anonymous", "Anonymous user")

## @brief Decorator class designed to register user authentication methods
#
# Example : 
# <pre>
# @authentication_method
# def foo_auth(identity, proof):
#   if ok:
#       return True
#   else:
#       return False
# </pre>
#
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
    # @param identity * : user id
    # @param proof * : user authentication proof
    # @return False or a User Identity instance
    @classmethod
    def authenticate(cls, identifier, proof):
        if len(cls.__methods) == 0:
            raise RuntimeError("Not authentication method registered")
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


## @brief Decorator class designed to register identification methods
#
# The decorated methods should take one client_infos argument and returns a UserIdentity instance
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
    # @param datas * :  datas that may identify a user
    # @return False if identification fails, else returns an UserIdentity instance
    @classmethod
    def identify(cls, client_infos):
        if len(cls.__methods) == 0:
            raise RuntimeError("Not identification method registered")
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
                        return ret
                    res = ret
        return res


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
    # @param client str : client id (typically IP addr)
    # @param login str|None : given when a client try to be authenticated
    # @param proof str|None : given when a client try to be authenticated
    # @param **kwargs dict : context
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
            cls.__identity = anonymous_user if ret is False else ret
        return cls.__identity

    ## @brief authenticate a user
    # @param identifier * : user identifier
    # @param proof * : proof of identity
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
