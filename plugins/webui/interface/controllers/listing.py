# -*- coding: utf-8 -*-
from .base import get_response
import leapi_dyncode as dyncode

def list_classes(request):
    template_vars = {'my_classes': dyncode.dynclasses}
    return get_response('listing/list_classes.html', tpl_vars=template_vars)

def show_class(request):
    templates_var = {
        'params': request.GET
    }
    return get_response('listing/show_class.html', tpl_vars=template_vars)

def show_object(request):
    templates_var = {
        'params': request.GET
    }
    return get_response('listing/show_object.html', tpl_vars=template_vars)