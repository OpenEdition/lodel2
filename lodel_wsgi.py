import re
from urllib.parse import parse_qs

from Interface.web.controllers import *
from Interface.web.urls import urls


def application(env, start_response):

    values = {}

    # Querystring
    values['GET'] = parse_qs(env.get('QUERY_STRING'))

    # POST Values
    values['POST'] = parse_qs(env.get('wsgi.input').read())

    print(values)

    # URL Args
    path = env.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            env['url_args'] = match.groups()
            return callback(env, start_response)
    return not_found(env, start_response)