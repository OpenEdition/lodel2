#-*- conding: utf-8 -*-

from Lodel.hooks import LodelHook
from Lodel.user import UserContext

class PermissionDenied(Exception): pass

@LodelHook('leapi_get_pre')
def check_anon(hook_name, caller, payload):
    if not UserContext.identity().is_identified:
        raise PermissionDenied("Anonymous user's are not allowed to get content")

@LodelHook('leapi_update_pre')
@LodelHook('leapi_delete_pre')
@LodelHook('leapi_insert_pre')
def check_auth(hook_name, caller, payload):
    if not UserContext.identity().is_authenticated:
        raise PermissionDenied("Only authenticated user's are allowed to do that !")
