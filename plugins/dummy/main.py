#-*- coding: utf-8 -*-

from lodel.plugin import LodelHook

## @brief Hook's callback example
@LodelHook('leapi_get_pre')
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
