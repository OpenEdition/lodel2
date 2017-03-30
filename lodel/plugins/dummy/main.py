#-*- coding: utf-8 -*-

## @package lodel.plugins.dummy.main Plugin's loader module

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin': ['LodelHook', 'CustomMethod'],
    'lodel.settings' : 'settings'})


## @brief callback method using lodel's hook system
# @param hook_name str
# @param caller function : action to perform
# @param payload : data to pass to the caller
# @return payload
@LodelHook('leapi_get_post')
@LodelHook('leapi_update_pre')
@LodelHook('leapi_update_post')
@LodelHook('leapi_delete_pre')
@LodelHook('leapi_delete_post')
@LodelHook('leapi_insert_pre')
@LodelHook('leapi_insert_post')
def dummy_callback(hook_name, caller, payload):
    if settings.Settings.debug:
        print("\tHook %s\tcaller %s with %s" % (hook_name, caller, payload))
    return payload

## @brief instance method
# This is an example of a basic plugin's custom method
@CustomMethod('Object', 'dummy_method')
def dummy_instance_method(self):
    print("Hello world !\
I'm a custom method on an instance of class %s" % self.__class__)


## @brief instance method
# This is an example of a basic plugin's custom method
@CustomMethod('Object', 'dummy_class_method', CustomMethod.CLASS_METHOD)
def dummy_instance_method(self):
    print("Hello world !\
I'm a custom method on class %s" % self.__class__)
