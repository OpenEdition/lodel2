#-*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin': ['LodelHook', 'CustomMethod']})

@LodelHook('leapi_get_post')
@LodelHook('leapi_update_pre')
@LodelHook('leapi_update_post')
@LodelHook('leapi_delete_pre')
@LodelHook('leapi_delete_post')
@LodelHook('leapi_insert_pre')
@LodelHook('leapi_insert_post')
def dummy_callback(hook_name, caller, payload):
    if Lodel.settings.Settings.debug:
        print("\tHook %s\tcaller %s with %s" % (hook_name, caller, payload))
    return payload


@CustomMethod('Object', 'dummy_method')
def dummy_instance_method(self):
    print("Hello world !\
I'm a custom method on an instance of class %s" % self.__class__)


@CustomMethod('Object', 'dummy_class_method', CustomMethod.CLASS_METHOD)
def dummy_instance_method(self):
    print("Hello world !\
I'm a custom method on class %s" % self.__class__)
