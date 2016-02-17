# -*- coding: utf-8 -*-
from ...Template.Loader import TemplateLoader

# This module contains the web UI controllers that will be called from the WebUI class


response_codes = {
    '200': '200 OK',
    '404': '404 NOT FOUND'
}


def admin(request, start_response):
    start_response(response_codes['200'], [('Content-Type', 'text/html')])
    loader = TemplateLoader()
    return [loader.render_to_response('Lodel/templates/admin/admin.html')]


def index(request, start_response):
    start_response(response_codes['200'], [('Content-Type', 'text/html')])
    loader = TemplateLoader()
    return [loader.render_to_response('Lodel/templates/index/index.html')]


def not_found(request, start_response):
    start_response(response_codes['404'], [('Content-Type', 'text/html')])
    loader = TemplateLoader()
    return [loader.render_to_response('Lodel/templates/errors/404.html')]
