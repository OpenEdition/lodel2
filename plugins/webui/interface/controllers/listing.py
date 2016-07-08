# -*- coding: utf-8 -*-
from .base import get_response
import leapi_dyncode as dyncode

def list_classes(request):
    template_vars = {'my_classes': dyncode.dynclasses}
    return get_response('listing/list_classes.html', my_classes=dyncode.dynclasses)

def show_class(request):
    if 'classname' in request.GET:
        classname = request.GET['classname']
        if len(classname) > 1:
            raise HttpException(400)
        classname = classname[0]
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
    return get_response('listing/show_class.html', classname=classname)

def show_object(request):
    template_vars = {
        'params': request.GET
    }
    test_valid = 'lodel_id' in request.GET \
        and len(request.GET['lodel_id']) == 1

    if test_valid:
        try:
            lodel_id = int(request.GET['lodel_id'][0])
        except (ValueError, TypeError):
            test_valid = False

    if not test_valid:
        raise HttpException(400)
    else:
        obj = dyncode.Object.get(['lodel_id = %d' % lodel_id])
        if len(obj) == 0:
            raise HttpException(404)
    if 'classname' in request.GET:
        classname = request.GET['classname']
        if len(classname) > 1:
            raise HttpException(400)
        classname = classname[0]
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
    return get_response('listing/show_object.html', lodel_id=lodel_id, classname=classname)