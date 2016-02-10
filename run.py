# -*- coding: utf-8 -*-
from importlib import import_module
import re
from urllib.parse import parse_qs

from Modules.Interface.web.controllers import *
from Modules.Interface.web.urls import urls


# TODO Placer cette conf dans les settings lodel
installed_plugins = ['testmod']


def get_plugins_routes(installed_plugins):
    routes = []
    for url in urls:
        routes.append((url[0], url[1]))

    for installed_plugin in installed_plugins:
        try:
            mod = import_module('Plugins.%s.urls' % installed_plugin)
            app_routes = getattr(mod, 'urls')
            for app_route in app_routes:
                routes.append(app_route)
        except ImportError:
            continue

    return routes


def set_parsed_arguments(env):
    env['GET'] = parse_qs(env.get('QUERY_STRING'))
    env['POST'] = parse_qs(env.get('wsgi.input').read())
    env['PATH'] = env.get('PATH_INFO', '').lstrip('/')


def controller(env, routes):
    for regex, callback in routes:
        match = re.search(regex, env['PATH'])
        if match is not None:
            env['url_args'] = match.groups()
            return callback
    return not_found


# WSGI Application
def application(env, start_response):
    routes = get_plugins_routes(installed_plugins=installed_plugins)
    set_parsed_arguments(env)
    print(env['GET'], env['POST'], env['PATH'])
    view = controller(env, routes)
    return view(env, start_response)