# -*- coding: utf-8 -*-
import cgi
from urllib.parse import parse_qs


## @brief parses a wsgi request's querystring, post values and files
#
# @param env dict : request
# @return dict
def parse_request(env):

    env['PATH'] = env.get('PATH_INFO', '').lstrip('/')
    env['GET'] = {}
    env['POST'] = {}
    env['FILES'] = {}

    if 'HTTP_COOKIE' in env:
        cookie_string = env['HTTP_COOKIE']
        cookie_elements = cookie_string.split('; ')
        env['HTTP_COOKIE'] = {}
        for cookie_element in cookie_elements:
            cookie_split = cookie_element.split('=')
            env['HTTP_COOKIE'][cookie_split[0]] = cookie_split[1]

        if 'sid' in env['HTTP_COOKIE']:
            env['SESSION_ID'] = env['HTTP_COOKIE']['sid']

    arg_fields = cgi.FieldStorage(fp=env['wsgi.input'], environ=env, keep_blank_values=True)

    for arg_field in arg_fields.list:
        if isinstance(arg_field, cgi.MiniFieldStorage):
            # Querystring argument
            name = arg_field.name
            value = arg_field.value
            if name.endswith('[]'):
                if name not in env['GET']:
                    env['GET'][name] = arg_fields.getlist(name)
            else:
                env['GET'][name] = value
        else:
            # Post argument
            name = arg_field.disposition_options['name']
            filename = arg_field.disposition_options['filename'] if 'filename' in arg_field.disposition_options else None
            if filename is not None:
                value = arg_field.file.read()
                if name.endswith('[]'):
                    if name not in env['FILES']:
                        env['FILES'][name] = []
                    env['FILES'][name].append({'filename': filename, 'content': value})
                else:
                    env['FILES'][name] = {'filename': filename, 'content': value}
            else:
                if name.endswith('[]'):
                    if name not in env['FILES']:
                        env['POST'][name] = arg_fields.getlist(name)
                else:
                    env['POST'][name] = arg_fields.getvalue(name)

    return env
