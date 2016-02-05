#-*- coding: utf-8 -*-

import types
import importlib
from libs.transwrap.transwrap import DefaultCallCatcher

## @brief Example implementation of an ACL class
class ACL(DefaultCallCatcher):
    _singleton = None
    
    ## @brief dummy singleton contructor
    def __init__(self, **kwargs):
        ACL._singleton = self
    
    ## @brief dummy singleton getter
    @classmethod
    def instance(cls):
        if cls._singleton is None:
            cls()
        return cls._singleton

    ## @brief Method designed to be called when an access is done on a wrapped class
    # @note fetch the attribute
    # @param obj : the python object on wich the access is done
    # @param attr_name str : the name of the accessed attribute
    # @return the attribute
    # @throw AttributeError if the attr does not exist
    @classmethod
    def attr_get(cls, obj, attr_name):
        return cls.instance()._attr_get(obj, attr_name)

    ## @brief Method designed to be called when a wrapped class method is called
    # @note Do the call
    # @param obj : the python object the method belongs to
    # @param method : the python bound method
    # @param args tuple : method call positional arguments
    # @param kwargs dict : method call named arguments
    # @return the call returned value
    @classmethod
    def method_call(cls, obj, method, args, kwargs):
        return cls.instance()._method_call(obj, method, args, kwargs)

    ## @brief instance implementation of attr_get()
    def _attr_get(self, obj, attr_name):
        if hasattr(obj, '__name__'):
            print("\tCatched ! %s.%s"  % (obj.__name__, attr_name))
        else:
            print("\tCatched ! Get %s.%s"  % (obj, attr_name))
        return super().attr_get(obj, attr_name)

    ## @brief instance implementation of method_call()
    def _method_call(self, obj, method, args, kwargs):
        if obj is method:
            print("\tCatched ! %s(%s %s)" % (obj.__name__, args, kwargs))
        else:
            if hasattr(obj, '__name__'):
                print("\tCatched ! %s.%s(%s %s)" % (obj.__name__, method.__name__, args,kwargs))
            else:
                print("\tCatched ! %s.%s(%s %s)" % (obj, method.__name__, args,kwargs))
            print("\t\tCallobject = %s method = %s with %s %s" % (obj, method, args, kwargs))
        return super().method_call(obj, method, args, kwargs)
