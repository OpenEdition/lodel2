# -*- coding: utf-8 -*-
from ...Template.Loader import TemplateLoader
from werkzeug.wrappers import Response
# This module contains the web UI controllers that will be called from the WebUI class


def admin(request, start_response):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/admin/admin.html'), mimetype='text/html')
    response.set_cookie('name', 'value')
    response.set_cookie('name2', 'value2')
    response.status_code = 200
    return response(request, start_response)


def index(request, start_response):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/index/index.html'), mimetype='text/html')
    response.status_code = 200
    return response(request, start_response)


def not_found(request, start_response):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/errors/404.html'), mimetype='text/html')
    response.status_code = 404
    return response(request, start_response)


def test(request, start_response):
    loader = TemplateLoader()
    response = Response(loader.render_to_response('Lodel/templates/test.html'), mimetype='text/html')
    response.status_code = 200
    return response(request, start_response)
