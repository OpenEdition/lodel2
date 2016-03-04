# -*- coding: utf-8 -*-
from ...Template.Loader import TemplateLoader
from werkzeug.wrappers import Response
# This module contains the web UI controllers that will be called from the WebUI class


def admin(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/admin/admin.html'), mimetype='text/html')
    response.status_code = 200
    return response


def index(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/index/index.html'), mimetype='text/html')
    response.status_code = 200
    return response


def not_found(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/errors/404.html'), mimetype='text/html')
    response.status_code = 404
    return response


def test(request):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/test.html'), mimetype='text/html')
    response.status_code = 200
    return response
