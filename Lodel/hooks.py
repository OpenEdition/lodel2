#-*- coding: utf-8 -*-

import os
import copy
from importlib.machinery import SourceFileLoader

from Lodel.settings import Settings

## @brief Class designed to handle a hook's callback with a priority
class DecoratedWrapper(object):
    ## @brief Constructor
    # @param hook function : the function to wrap
    # @param priority int : the callbacl priority
    def __init__(self, hook, priority):
        self._priority = priority
        self._hook = hook
    
    ## @brief Call the callback
    # @param *args
    # @param **kwargs
    # @return modified payload
    def __call__(self, hook_name, caller, payload):
        return self._hook(hook_name, caller, payload)

## @brief Decorator designed to register hook's callbacks
#
# Example : 
#
# <pre>
# @LodelHook('hook_name', 42)
# def super_callback(hook_name, caller, payload):
#    return payload
#
# LodelHook.call_hook('hook_name', caller, 'foobar') #calls super_callback('hook_name', caller, 'foobar')
# </pre>
class LodelHook(object):
    
    ## @brief Stores all hooks (DecoratedWrapper instances)
    _hooks = dict()
    
    ## @brief Decorator constructor
    # @param hook_name str : the name of the hook to register to
    # @param priority int : the hook priority
    def __init__(self, hook_name, priority = None):
        self._hook_name = hook_name
        self._priority = 0xFFFF if priority is None else priority
    
    ## @brief called just after __init__
    # @param hook function : the decorated function
    # @return the hook argument
    def __call__(self, hook):
        if not self._hook_name in self._hooks:
            self._hooks[self._hook_name] = list()
        wrapped = DecoratedWrapper(hook, self._priority)
        self._hooks[self._hook_name].append(wrapped)
        self._hooks[self._hook_name] = sorted(self._hooks[self._hook_name], key = lambda h: h._priority)
        return hook

    ## @brief Call hooks
    # @param hook_name str : the hook's name
    # @param payload * : datas for the hook
    # @return modified payload
    @classmethod
    def call_hook(cls, hook_name, caller, payload):
        if hook_name in cls._hooks:
            for hook in cls._hooks[hook_name]:
                payload = hook(hook_name, caller, payload)
        return payload
    
    ## @brief Fetch registered hooks
    # @param names list | None : optionnal filter on name
    # @return a list of functions
    @classmethod
    def hook_list(cls, names = None):
        res = None
        if names is not None:
            res = { name: copy.copy(cls._hooks[name]) for name in cls._hooks if name in names}
        else:
            res = copy.copy(cls._hooks)
        return { name: [(hook._hook, hook._priority) for hook in hooks] for name, hooks in res.items() }
    
    ## @brief Unregister all hooks
    # @warning REALLY NOT a good idea !
    # @note implemented for testing purpose
    @classmethod
    def __reset__(cls):
        cls._hooks = dict()