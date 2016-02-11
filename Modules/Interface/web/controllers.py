# -*- coding: utf-8 -*-
from ...Template.Loader import TemplateLoader

# This module contains the web UI controllers that will be called from the WebUI class


response_codes = {
    '200': '200 OK',
    '404': '404 NOT FOUND'
}


def admin(request, start_response):
    start_response(response_codes['200'], [('Content-Type', 'text/html')])
    return [b"ADMIN"]


def index(request, start_response):
    start_response(response_codes['200'], [('Content-Type', 'text/html')])
    return [b"DASHBOARD"]


def not_found(request, start_response):
    start_response(response_codes['404'], [('Content-Type', 'text/plain')])
    return [b'Not Found']
