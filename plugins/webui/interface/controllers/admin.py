from ...exceptions import *
from .base import get_response

from lodel.leapi.exceptions import *
from lodel import logger

from ...client import WebUiClient
import leapi_dyncode as dyncode
import warnings

def index_admin(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
    return get_response('admin/admin.html')

def admin_update(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
    msg=''
    if request.method == 'POST':
        error = None
        datas = list()
        classname = request.form['classname']
        logger.warning('Composed uids broken here')
        uid = request.form['uid']
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            classname = None
        if classname is None or target_leo.is_abstract():
            raise HttpException(400)
        fieldnames = target_leo.fieldnames()

        uid_field = target_leo.uid_fieldname()[0]
        fields = dict()

        for in_put, in_value in request.form.items():
            if in_put != 'classname' and  in_put != 'uid':
                dhl = target_leo.data_handler(in_put[12:])
                if dhl.is_reference() and in_value != '':
                    in_value.replace(" ","")
                    in_value=in_value.split(',')
                    in_value=list(in_value)
                if in_value != '':
                    fields[in_put[12:]] = in_value

        filter_q = '%s = %s' % (uid_field, uid)
        obj = (target_leo.get((filter_q)))[0]

        inserted = obj.update(fields)
        
        if inserted==1:
            msg = 'Successfully updated';
        else:
            msg = 'Oops something wrong happened...object not saved'
        return get_response('admin/admin_edit.html', target=target_leo, uidfield = uid_field, lodel_id = uid, msg = msg)

    if 'classname' in request.GET:
        classname = request.GET['classname']
        if len(classname) > 1:
            raise HttpException(400)
        classname = classname[0]
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            # classname = None
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
    return get_response('admin/admin_edit.html', target=target_leo, lodel_id =lodel_id)

def admin_create(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
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
            if in_put != 'classname' and in_value != '':
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

def admin_delete(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
    classname = None

    if 'classname' in request.GET:
        classname = request.GET['classname']
        if len(classname) > 1:
            raise HttpException(400)
        classname = classname[0]
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            # classname = None
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
        nb_deleted = target_leo.delete_bundle(query_filters)

    if nb_deleted == 1:
            msg = 'Object successfully deleted';
    else:
            msg = 'Oops something wrong happened...object still here'
            
    return get_response('admin/admin_delete.html', target=target_leo, lodel_id =lodel_id, msg = msg)

        
        
def admin_classes(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
    return get_response('admin/list_classes_admin.html', my_classes = dyncode.dynclasses)

def create_object(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
    return get_response('admin/list_classes_create.html', my_classes = dyncode.dynclasses)

def delete_object(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
    return get_response('admin/list_classes_delete.html', my_classes = dyncode.dynclasses)
    
def admin_class(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
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

def delete_in_class(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
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
    return get_response('admin/show_class_delete.html', target=target_leo)

def admin(request):
    if WebUiClient.is_anonymous():
        return get_response('users/signin.html')
    return get_response('admin/admin.html')

        
            

