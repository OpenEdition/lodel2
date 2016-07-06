# -*- coding: utf-8 -*-
import re

from .controllers import *
from .urls import urls
from ..main import root_url
from lodel.settings import Settings

def format_url_rule(url_rule):
    if url_rule.startswith('^'):
        res = url_rule.replace('^', '^'+root_url())
    else:
        res = root_url()+'.*'+url_rule
    return res


def get_controller(request):

    url_rules = []
    for url in urls:
        url_rules.append((format_url_rule(url[0]), url[1]))

    # Returning the right controller to call
    for regex, callback in url_rules:
        p = re.compile(regex)
        m = p.search(request.PATH)
        if m is not None:
            request.url_args = m.groupdict()
            return callback

    return not_found
