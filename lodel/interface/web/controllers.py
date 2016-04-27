# -*- coding: utf-8 -*-
from werkzeug.wrappers import Response
from lodel.template.loader import TemplateLoader

# This module contains the web UI controllers that will be called from the web ui class

def admin(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('templates/admin/admin.html'), mimetype='text/html')
    response.status_code = 200
    return response


def index(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('templates/index/index.html'), mimetype='text/html')
    response.status_code = 200
    return response


def not_found(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('templates/errors/404.html'), mimetype='text/html')
    response.status_code = 404
    return response


def test(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('templates/test.html'), mimetype='text/html')
    response.status_code = 200
    return response