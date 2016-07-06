from ...exceptions import *
from .base import get_response

from lodel.leapi.exceptions import *
from lodel import logger

import leapi_dyncode as dyncode
import warnings
from lodel import logger

def index_admin(request):
    return get_response('admin/admin.html')

def admin_update(request):
    msg=''
    if request.method == 'POST':

        error = None
        datas = list()
        classname = request.form['classname']
        uid = request.form['uid']
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
        if classname is None or target_leo.is_abstract():
            raise HttpException(400)
        fieldnames = target_leo.fieldnames()
        fields = dict()

        for in_put, in_value in request.form.items():
            if in_put != 'classname' and  in_put != 'uid':
                fields[in_put[12:]] = in_value
        obj = (target_leo.get(('lodel_id = %s' % (uid))))[0]
        inserted = obj.update(fields)
        
        if inserted==1:
            msg = 'Successfully updated';
        else:
            msg = 'Oops something wrong happened...object not saved'
        return get_response('admin/admin_edit.html', target=target_leo, lodel_id = uid, msg = msg)

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

    return get_response('admin/admin_edit.html', target=target_leo, lodel_id =lodel_id)

def admin_create(request):
    classname = None

    if request.method == 'POST':
        error = None
        datas = list()
        classname = request.form['classname']
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
        if classname is None or target_leo.is_abstract():
            raise HttpException(400)
        fieldnames = target_leo.fieldnames()
        fields = dict()

        for in_put, in_value in request.form.items():
            if in_put != 'classname':
                fields[in_put[12:]] = in_value
        new_uid = target_leo.insert(fields)
        
        if not new_uid is None:
            msg = 'Successfull creation';
        else:
            msg = 'Oops something wrong happened...object not saved'
        return get_response('admin/admin_create.html', target=target_leo, msg = msg)
    
    if 'classname' in request.GET:
        classname = request.GET['classname']
        if len(classname) > 1:
            raise HttpException(400)
        classname = classname[0]
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
    msg = None
    if 'msg' in request.GET:
        msg = request.GET['msg']
    if classname is None or target_leo.is_abstract():
        raise HttpException(400)
    return get_response('admin/admin_create.html', target=target_leo)

def admin_classes(request):
    return get_response('admin/list_classes_admin.html', my_classes = dyncode.dynclasses)

def admin_class(request):
    if 'classname' in request.GET:
        classname = request.GET['classname']
        if len(classname) > 1:
            raise HttpException(400)
        classname = classname[0]
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
    if classname is None or target_leo.is_abstract():
        raise HttpException(400)
    return get_response('admin/show_class_admin.html', target=target_leo)
   
def admin(request):
    return get_response('admin/admin.html')

        
            

