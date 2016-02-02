#-*- coding: utf-8 -*-

import types
import importlib

## @brief Example implementation of an ACL class
class ACL(object):
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

    ## @brief Callback that checks a call to wrapped classes methods
    @classmethod
    def check_call(cls, call_object, method_name, args, kwargs):
        return ACL.instance()._check_call(call_object, method_name, args, kwargs)

    ## @brief Callback that checks calls to wrapped classes attributes
    @classmethod
    def check_attr(cls, call_object, attr_name):
        return ACL.instance()._check_attr(call_object, attr_name)

    ## @brief instance version of check_attr()
    # @note this method is the one that fetch and return the attribute
    def _check_attr(self, call_object, attr_name):
        print("Getting attribute '%s' on %s" % (attr_name, call_object))
        return getattr(call_object, attr_name)

    ## @brief instance version of check_call()
    # @note this method is the one that call the method and return the returned value
    # @param call_object : the object on wich the method is called (class if class methode else instance)
    # @param method_name str : method name
    # @param *args : positional method arguments
    # @param **kwargs : keyword method arguments
    def _check_call(self, call_object, method_name, args, kwargs):
        print("Calling '%s' on %s with %s %s" % (method_name, call_object, args, kwargs))
        #return call_object.__getattribute__(method_name)(*args, **kwargs)
        if method_name == '__init__':
            return call_object(*args, **kwargs)
        return getattr(call_object, method_name)(*args, **kwargs)


## @brief A class designed as a wrapper for a method
class AclMethodWrapper(object):
    
    ## @brief Constructor
    # @param wrapped_object PythonClass : A python class
    # @param method_name str : the wrapped method name
    def __init__(self, wrapped_object, method_name):
        self._wrapped_object = wrapped_object
        self._method_name = method_name

    ## @brief Triggered when the wrapped method is called
    def __call__(self, *args, **kwargs):
        return ACL.check_call(self._wrapped_object, self._method_name, args, kwargs)

## @brief Return a wrapped class
#
# @param module_name str : LeAPI dyn mopdule name
# @param wrapped_class_name str : wrapped class name
def get_wrapper(module_name, wrapped_class_name):
    
    module = importlib.import_module(module_name)
    wrapped_class = getattr(module, wrapped_class_name)

    ## @brief Meta class that handles accesses to wrapped class/static attributes
    class MetaAclWrapper(type):
        ## @brief Called when we get a class attribute
        def __getattribute__(cls, name):
            try:
                attr = getattr(wrapped_class, name)
                if isinstance(attr, types.MethodType):
                    return AclMethodWrapper(wrapped_class, name)
                else:
                    return ACL.check_attr(wrapped_class, name)
            except Exception as e:
                #Here we can process the exception or log it
                raise e

    #class AclWrapper(metaclass=MetaAclWrapper):
    class AclWrapper(object, metaclass=MetaAclWrapper):

        def __init__(self, *args, **kwargs):
            self._wrapped_instance = ACL.check_call(wrapped_class, '__init__', args, kwargs)
            #self._wrapped_instance = wrapped_class(*args, **kwargs)

        def __getattribute__(self, name):
            try:
                attr = getattr(
                    super().__getattribute__('_wrapped_instance'),
                    name
                )
                if isinstance(attr, types.MethodType):
                    return AclMethodWrapper(super().__getattribute__('_wrapped_instance'), name)
                else:
                    return ACL.check_attr(super().__getattribute__('_wrapped_instance'), name)
            except Exception as e:
                #do what you want
                raise e
    return AclWrapper

