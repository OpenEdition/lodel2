# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {'lodel.logger': 'logger'})
LodelContext.expose_dyncode(globals(), 'dyncode')

from .base import get_response
from .utils import *
from ...exceptions import *

##@brief These functions are called by the rules defined in ../urls.py
## To browse the editorial model

##@brief Controller's function to list all types (classes) of the editorial model
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
def list_classes(request):
    if 'allclasses' in request.GET:
        allclasses = request.GET['allclasses']
    else:
        allclasses = 1
    return get_response('listing/list_classes.html', my_classes=dyncode.dynclasses, allclasses = allclasses)

##@brief Controller's function to list all types (classes) of the editorial model
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
def collections(request):
    return get_response('listing/collections.html', my_classes=dyncode, get_authors=get_authors)

##@brief Controller's function to list all types (classes) of the editorial model
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
def issue(request):
    lodel_id = request.GET['lodel_id']
    return get_response('listing/issue.html', lodel_id=lodel_id[0], my_classes=dyncode )

##@brief Controller's function to display a type (class) of the editorial model
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
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

##@brief Controller's function to display an instance or a certain type
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
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

##@brief Controller's function to display an instance or a certain type
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
def show_object_detailled(request):
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

    return get_response('listing/show_object_detailled.html', lodel_id=lodel_id, classname=classname)
