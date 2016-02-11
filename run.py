# -*- coding: utf-8 -*-
from Modules.Interface.web.router import get_controller


# WSGI Application
def application(env, start_response):
    controller = get_controller(env)
    return controller(env, start_response)
