#-*- coding: utf-8 -*-

## @package libs.transwrap A lib designed to be a wrapper for any class
#
#

import types
from .magix import MAGIX

class DefaultCallCatcher(object):
        
    @classmethod
    def attr_get(self, obj, attr_name):
        if hasattr(obj, '__name__'):
            print("\tCatched ! %s.%s"  % (obj.__name__, attr_name))
        else:
            print("\tCatched ! Get %s.%s"  % (obj, attr_name))
        return getattr(obj, attr_name)
    
    @classmethod
    def method_call(self, obj, method, args, kwargs):
        if obj is method:
            print("\tCatched ! %s(%s %s)" % (obj.__name__, args, kwargs))
        else:
            if hasattr(obj, '__name__'):
                print("\tCatched ! %s.%s(%s %s)" % (obj.__name__, method.__name__, args,kwargs))
            else:
                print("\tCatched ! %s.%s(%s %s)" % (obj, method.__name__, args,kwargs))
            print("\t\tCallobject = %s method = %s with %s %s" % (obj, method, args, kwargs))

        return method(*args, **kwargs)

def get_wrap(towrap, call_catcher_cls = DefaultCallCatcher):
    
    class funwrap(object):
        
        def __init__(self, obj, fun):
            self._fun = fun
            self._obj = obj
        
        def __call__(self, *args, **kwargs):
            return call_catcher_cls.method_call(self._obj, self._fun, args, kwargs)
        
        def __repr__(self):
            return '<funwrap %s>' % self._fun

    class metawrap(type):
            
        def __getattribute__(self, name):
            try:
                attr = getattr(towrap,name)
                if callable(attr):
                    return funwrap(towrap, attr)
                else:
                    return call_catcher_cls.attr_get(towrap, name)
            except Exception as e:
                raise e

    class wrap(object, metaclass=metawrap):

        def __init__(self, *args, **kwargs):
            super().__setattr__('_instance', call_catcher_cls.method_call(towrap, towrap, args, kwargs))

        def __getattribute__(self, name):
            try:
                instance = super().__getattribute__('_instance')
                attr = call_catcher_cls.attr_get(instance, name)
                if name == '__class__': # !!! important !!! isinstance call catch
                    return towrap
                if callable(attr):
                    ret = funwrap(instance, attr)
                    return ret
                return attr
            except Exception as e:
                print("Failed get instance on", name)
                raise e

    ## @brief Magic method instance magic wrap method generator
    # @return A magic method designed to be injected in wrap
    def make_instance_magix(name):
        def magix_instance_wrap(self, *args, **kwargs):
            instance = object.__getattribute__(self, '_instance')
            try:
                method = getattr(instance, name)
            except AttributeError as expt: # catch __del__ call on instances
                return None
            return call_catcher_cls.method_call(instance, method, args, kwargs)
        return magix_instance_wrap

    ## @brief Magic method instance magic wrap method generator
    # @return A magic method designed to be injected in a metawrap
    def make_class_magix(name):
        def magix_class_wrap(self, *args, **kwargs):
            args = tuple([towrap] + list(args))
            try:
                method = getattr(towrap.__class__, name)
            except AttributeError as e: # catch __del__ call on instances
                return None
            return call_catcher_cls.method_call(towrap.__class__, method, args, kwargs)
        return magix_class_wrap

    instance_ex = ['__init__', '__new__'] # exclude for instances
    class_ex = ['__new__'] # exclude for classes
    for name in MAGIX:
        if name not in instance_ex:
            setattr(wrap, name, make_instance_magix(name))
        if name not in class_ex:
            setattr(metawrap, name, make_class_magix(name))
            
    return wrap
