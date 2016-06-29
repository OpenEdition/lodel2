# -*- coding: utf-8 -*-

from werkzeug.wrappers import Response
from ..template.loader import TemplateLoader

# This module contains the web UI controllers that will be called from the web ui class


def get_response(tpl, mimetype='text/html', status_code=200):
    loader = TemplateLoader()
    response = Response(loader.render_to_response(tpl), mimetype=mimetype)
    response.status_code = status_code
    return response


def index(request):
    return get_response('index/index.html')


def not_found(request):
    return get_response('errors/404.html', status_code=404)


def test(request):
    return get_response('test.html')


def list_classes(request):
    # TODO Add the method to get the classes list

    return get_response('list_classes.html')
