# -*- coding: utf-8 -*-
import re

from .controllers import *
from .urls import urls
from lodel.settings import Settings


def format_url_rule(url_rule):
    if url_rule == '^$':
        return "^%s$" % Settings.sitename

    formatted_rule = ''
    if url_rule.startswith('^'):
        formatted_rule += "^"

    formatted_rule += "%s/%s" % (Settings.sitename, url_rule)
    return formatted_rule


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
        '''match = re.search(regex, request.PATH)
        if match is not None:
            request.url_args = match.groups()
            return callback
        '''
    return not_found
