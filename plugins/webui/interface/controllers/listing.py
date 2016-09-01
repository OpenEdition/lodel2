# -*- coding: utf-8 -*-
from .base import get_response
from ...exceptions import *
from lodel import logger
import leapi_dyncode as dyncode

def list_classes(request):
    if 'allclasses' in request.GET:
        allclasses = request.GET['allclasses']
    else:
        allclasses = 1
    return get_response('listing/list_classes.html', my_classes=dyncode.dynclasses, allclasses = allclasses)

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
    else:
        raise HttpException(400)
    return get_response('listing/show_class.html', classname=classname)

def show_object(request):
    if 'classname' in request.GET:
        classname = request.GET['classname']
        if len(classname) > 1:
            raise HttpException(400)
        classname = classname[0]
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
    else:
        raise HttpException(400)
    
    logger.warning('Composed uids broken here')
    uid_field = target_leo.uid_fieldname()[0]

    test_valid = 'lodel_id' in request.GET \
        and len(request.GET['lodel_id']) == 1

    if test_valid:
        try:
            dh = target_leo.field(uid_field)
            lodel_id = dh.cast_type(request.GET['lodel_id'][0])
        except (ValueError, TypeError):
            test_valid = False

    if not test_valid:
        raise HttpException(400)
    else:
        query_filters = list()
        query_filters.append((uid_field,'=',lodel_id))
        obj = target_leo.get(query_filters)
        if len(obj) == 0:
            raise HttpException(404)

    return get_response('listing/show_object.html', lodel_id=lodel_id, classname=classname)
