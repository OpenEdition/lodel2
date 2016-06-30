from ...exceptions import *
from .base import get_response

from lodel.leapi.exceptions import *
from lodel import logger

import leapi_dyncode as dyncode

def index_admin(request):
    return get_response('admin/admin.html')

def admin_update(request):
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
    print("WHAT WE GOT AS RESPONSE : ")
    for n,o in enumerate(obj):
        print("\t",n,o.datas(True))
    return get_response('admin/admin_edit.html', obj = obj)

def admin_create(request):
    classname = None
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
    
    return get_response('admin/admin_create.html', target=target_leo)

def admin(request):
    return get_response('admin/admin.html')


