# -*- coding: utf-8 -*-

from werkzeug.wrappers import Response
from ..template.loader import TemplateLoader

# This module contains the web UI controllers that will be called from the web ui class


def get_response(tpl, tpl_vars={}, mimetype='text/html', status_code=200):
    loader = TemplateLoader()
    response = Response(loader.render_to_response(tpl, template_vars=tpl_vars), mimetype=mimetype)
    response.status_code = status_code
    return response


def index(request):
    return get_response('index/index.html')


def not_found(request):
    return get_response('errors/404.html', status_code=404)


def test(request):
    template_vars = {
        'id': request.url_args['id'],
        'params': request.GET
    }
    return get_response('test.html', tpl_vars=template_vars)
    return get_response('test.html')
    
