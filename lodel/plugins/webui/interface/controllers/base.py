# -*- coding: utf-8 -*-

from werkzeug.wrappers import Response
from ..template.loader import TemplateLoader

# This module contains the web UI controllers that will be called from the web ui class

##@brief Render a template and return a respone
#@param tpl str : template relativ path
#@param tpl_vars : templates variables (obsolete)
#@param mimetype
#@param status_code
#@param **kwargs : new version of tpl_vars
#@return a response...
def get_response(tpl='empty.html', tpl_vars={}, mimetype='text/html', status_code=200, **kwargs):
    tpl_vars.update(kwargs)
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
    return get_response('listing/collection')


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
    
