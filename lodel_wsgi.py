import re

import Interface.web.controllers as controllers
import Interface.web.urls.urls as urls


def application(env, start_response):
    # Query string
    print(env.get('QUERY_STRING'))

    # URL Args
    path = env.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            env['url_args'] = match.groups()
            return controllers.callback(env, start_response)

    return controllers.not_found(env, start_response)