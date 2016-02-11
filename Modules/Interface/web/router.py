# -*- coding: utf-8 -*-
import re
from importlib import import_module
from urllib.parse import parse_qs

from Modules.Interface.web.controllers import *
import Modules.Interface.web.urls as main_urls


def get_controller(env):
    # Compile all url rules from the main application and from the plugins
    url_rules = []
    for url in main_urls.urls:
        url_rules.append((url[0], url[1]))

    # Parsing the request
    env['GET'] = parse_qs(env.get('QUERY_STRING'))
    env['POST'] = parse_qs(env.get('wsgi.input').read())
    env['PATH'] = env.get('PATH_INFO', '').lstrip('/')

    # Returning the right controller to call
    for regex, callback in url_rules:
        match = re.search(regex, env['PATH'])
        if match is not None:
            env['url_args'] = match.groups()
            return callback
    return not_found
