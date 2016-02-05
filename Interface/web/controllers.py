# -*- coding: utf-8 -*-
from Template.Loader import TemplateLoader

# This module contains the web UI controllers that will be called from the WebUI class


def admin(request, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["ADMIN"]


def index(request, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["DASHBOARD"]


def not_found(request, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']