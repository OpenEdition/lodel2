# -*- coding: utf-8 -*-
import re
from .LodelRequest import LodelRequest

from Modules.Interface.web.controllers import *
import Modules.Interface.web.urls as main_urls


def get_controller(env):
    request = LodelRequest(env)

    url_rules = []
    for url in main_urls.urls:
        url_rules.append((url[0], url[1]))

    # Returning the right controller to call
    for regex, callback in url_rules:
        match = re.search(regex, request.PATH)
        if match is not None:
            env['url_args'] = match.groups()
            return callback

    return not_found
