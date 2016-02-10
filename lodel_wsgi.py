# -*- coding: utf-8 -*-
from importlib import import_module
import re
from urllib.parse import parse_qs

from Interface.web.controllers import *
from Interface.web.urls import urls


def application(env, start_response):

    # TODO Placer cette conf dans les settings lodel
    installed_apps = [
        'testmod'
    ]

    # TODO Factoriser ce bloc de routing dans une classe dédiée
    routes = []
    for url in urls:
        routes.append((url[0], url[1]))

    for installed_app in installed_apps:
        try:
            mod = import_module('Plugins.%s.urls' % installed_app)
            app_routes = getattr(mod, 'urls')
            for app_route in app_routes:
                routes.append(app_route)
        except ImportError:
            continue

    # Querystring
    env['GET'] = parse_qs(env.get('QUERY_STRING'))
    # POST Values
    env['POST'] = parse_qs(env.get('wsgi.input').read())
    # URL Args
    path = env.get('PATH_INFO', '').lstrip('/')
    for regex, callback in routes:
        match = re.search(regex, path)
        if match is not None:
            env['url_args'] = match.groups()
            return callback(env, start_response)
    return not_found(env, start_response)