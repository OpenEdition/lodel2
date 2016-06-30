# -*- coding: utf-8 -*-

from werkzeug.wrappers import Response
from ..template.loader import TemplateLoader

# This module contains the web UI controllers that will be called from the web ui class

def get_response(tpl='empty.html', tpl_vars={}, mimetype='text/html', status_code=200):
    loader = TemplateLoader()
    response = Response(loader.render_to_response(tpl, template_vars=tpl_vars), mimetype=mimetype)
    response.status_code = status_code
    return response

## @brief gets the html template corresponding to a given component type
# @param type str : name of the component type
# @param params dict : extra parameters to customize the template
def get_component_html(type='text', params={}):
    params['type'] = type
    template_loader = TemplateLoader()
    return template_loader.render_to_html(template_file='components/components.html', template_vars=params)

def index(request):
    return get_response('index/index.html')


def not_found(request):
    return get_response('errors/404.html', status_code=404)


def test(request):
    if 'id' not in request.url_args:
        id = None
    else:
        id = request.url_args['id']

    template_vars = {
        'id': id,
        'params': request.GET
    }
    return get_response('test.html', tpl_vars=template_vars)
    
