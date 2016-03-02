# -*- coding: utf-8 -*-
import re
from .request import *

from Modules.Interface.web.controllers import *
import Modules.Interface.web.urls as main_urls


def get_controller(env):
    # Compile all url rules from the main application and from the plugins
    url_rules = []
    for url in main_urls.urls:
        url_rules.append((url[0], url[1]))

    env = parse_request(env)

    # Management of the user context
    if 'sid' in env['HTTP_COOKIES']:
        # Un usercontext est présent dans le cookie transmis par le navigateur
    else:
        # Aucun usercontext

    # Returning the right controller to call
    for regex, callback in url_rules:
        match = re.search(regex, env['PATH'])
        if match is not None:
            env['url_args'] = match.groups()
            return callback
    return not_found
