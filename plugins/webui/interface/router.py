# -*- coding: utf-8 -*-
import re

from .controllers import *
from .urls import urls


def get_controller(request):
    url_rules = []
    for url in urls:
        url_rules.append((url[0], url[1]))

    # Returning the right controller to call
    for regex, callback in url_rules:
        match = re.search(regex, request.PATH)
        if match is not None:
            request.url_args = match.groups()
            return callback

    return not_found
