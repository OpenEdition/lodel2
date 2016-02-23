#-*- conding: utf-8 -*-

from Lodel.hooks import LodelHook
from Lodel.user import UserContext

class PermissionDenied(Exception): pass

@LodelHook('leapi_get_pre', 1)
def check_anon(hook_name, caller, payload):
    if not UserContext.identity().is_identified:
        raise PermissionDenied("Anonymous user's are not allowed to get content")
    return payload

@LodelHook('leapi_update_pre', 1)
@LodelHook('leapi_delete_pre', 1)
@LodelHook('leapi_insert_pre', 1)
def check_auth(hook_name, caller, payload):
    if not UserContext.identity().is_authenticated:
        raise PermissionDenied("Only authenticated user's are allowed to do that !")
    return payload
