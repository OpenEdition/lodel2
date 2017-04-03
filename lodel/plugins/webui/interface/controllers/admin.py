# -*- coding: utf-8 -*-
from ...exceptions import *
from .base import get_response

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.leapi.exceptions': [],
    'lodel.logger': 'logger',
    'lodel.leapi.datahandlers.base_classes': ['MultipleRef'],
    'lodel.leapi.exceptions': ['LeApiDataCheckErrors'],
    'lodel.exceptions': ['LodelExceptions']})
LodelContext.expose_dyncode(globals(), 'dyncode')

from ...client import WebUiClient
import warnings

LIST_SEPARATOR = ','

##@brief These functions are called by the rules defined in ../urls.py
## To administrate the instance of the editorial model

##@brief Controller's function to redirect on the home page of the admin
# @param request : the request (get or post)
# @note the response is given in a html page called in get_response_function
def index_admin(request):
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    return get_response('admin/admin.html')

##@brief Controller's function to update an object of the editorial model
# @param request : the request (get or post)
# @note the response is given in a html page (in templates/admin) called in get_response_function
def admin_update(request):
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    msg=''

    data = process_form(request)
    if not(data is False):
        if 'lodel_id' not in data:
            raise HttpException(400)
        target_leo = dyncode.Object.name2class(data['classname'])
        leo = target_leo.get_from_uid(data['lodel_id'])
        if leo is None:
            raise HttpException(404,
                custom = 'No %s with id %s' % (
                    target_leo.__name__, data['lodel_id']))
        try:
            leo.update(
                { f:data[f] for f in data if f not in ('classname', 'lodel_id')})
        except LeApiDataCheckErrors as e:
            raise HttpErrors(
                title='Form validation errors', errors = e._exceptions)



    # Display of the form with the object's values to be updated
    if 'classname' in request.GET:
        # We need the class of the object to update
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

    # We need the uid of the object
    test_valid = 'lodel_id' in request.GET \
        and len(request.GET['lodel_id']) == 1

    if test_valid:
        try:
            dh = target_leo.field(uid_field)
            # we cast the uid extrated form the request to the adequate type
            # given by the datahandler of the uidfield's datahandler
            lodel_id = dh.cast_type(request.GET['lodel_id'][0])
        except (ValueError, TypeError):
            test_valid = False

    if not test_valid:
        raise HttpException(400)
    else:
        # Check if the object actually exists
        # We get it from the database
        query_filters = list()
        query_filters.append((uid_field,'=',lodel_id))
        obj = target_leo.get(query_filters)
        if len(obj) == 0:
            raise HttpException(404)
    return get_response('admin/admin_edit.html', target=target_leo, lodel_id =lodel_id)

##@brief Controller's function to create an object of the editorial model
# @param request : the request (get or post)
# @note the response is given in a html page (in templates/admin) called in get_response_function
def admin_create(request):
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')

    data = process_form(request)
    if not(data is False):
        target_leo = dyncode.Object.name2class(data['classname'])
        if 'lodel_id' in data:
            raise HttpException(400)
        try:
            new_uid = target_leo.insert(
                { f:data[f] for f in data if f != 'classname'})
        except LeApiDataCheckErrors as e:
            raise HttpErrors(
                title='Form validation errors', errors = e._exceptions)
        if new_uid is None:
            raise HttpException(400, "Creation fails")
        else:
            return get_response(
                'admin/admin_create.html', target=target_leo,
                msg = "Created with uid %s" % new_uid)

    # Display of an empty form
    if 'classname' in request.GET:
        # We need the class to create an object in
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

##@brief Controller's function to delete an object of the editorial model
# @param request : the request (get)
# @note the response is given in a html page (in templates/admin) called in get_response_function
def admin_delete(request):
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    classname = None

    if 'classname' in request.GET:
        # We need the class to delete an object in
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

    # We also need the uid of the object to delete
    test_valid = 'lodel_id' in request.GET \
        and len(request.GET['lodel_id']) == 1

    if test_valid:
        try:
            dh = target_leo.field(uid_field)
            # we cast the uid extrated form the request to the adequate type
            # given by the datahandler of the uidfield's datahandler
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
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    return get_response('admin/list_classes_admin.html', my_classes = dyncode.dynclasses)

def create_object(request):
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    return get_response('admin/list_classes_create.html', my_classes = dyncode.dynclasses)

def delete_object(request):
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    return get_response('admin/list_classes_delete.html', my_classes = dyncode.dynclasses)

def admin_class(request):
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    # We need the class we'll list to select the object to edit
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
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    # We need the class we'll list to select the object to delete
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
    # We have to be identified to admin the instance
    # temporary, the acl will be more restrictive
    #if WebUiClient.is_anonymous():
    #    return get_response('users/signin.html')
    return get_response('admin/admin.html')


def search_object(request):
    if request.method == 'POST':
        classname = request.POST['classname']
        searchstring = request.POST['searchstring']
        try:
            target_leo = dyncode.Object.name2class(classname)
        except LeApiError:
            raise HttpException(400)
        # TODO The get method must be implemented here
    return get_response('admin/admin_search.html', my_classes = dyncode.dynclasses)

##@brief Process a form POST and return the posted data
#@param request : the request object
#@return a dict with data as value and fieldname as key
def process_form(request):
    if request.method != 'POST':
        return False
    res = dict()
    errors = dict()
    #Fetch concerned LeObject
    if 'classname' not in request.form:
        logger.error("Received a form without classname !")
        raise HttpException(400)
    res['classname'] = classname = request.form['classname']
    try:
        target_leo = dyncode.Object.name2class(classname)
    except LeApiError:
        logger.error(
            "Received a form with an invalid leo name : '%s'" % classname)
        raise HttpException(400, "No leobject named '%s'" % classname)
    if target_leo.is_abstract():
        logger.error(
            "Received a form with an abstract leo : '%s'" % classname)
        raise HttpException(400, '%s is abstract' % classname)
    #Process input fields
    for fieldname, value in request.form.items():
        if fieldname == 'classname':
            continue
        elif fieldname == 'uid':
            fieldname = 'lodel_id' #wow
        elif fieldname.startswith('field_input_'):
            fieldname = fieldname[12:]
        try:
            dh = target_leo.data_handler(fieldname)
        except NameError as e:
            errors[fieldname] = e
            continue
        if dh.is_reference() and not dh.is_singlereference():
            #Converting multiple references fields
            value = value.strip()
            if len(value) == 0:
                #handling default value for empty string
                if hasattr(dh, 'default'):
                    value = dh.default
                else:
                    #if not explicit default value, enforcing default as
                    #an empty list
                    value = []
            else:
                value = [ v.strip() for v in value.split(LIST_SEPARATOR) ]
                value = [ v for v in value if len(v) > 0]
        else:
            #Handling default value for empty string
            if len(value.strip()) == 0 and hasattr(dh, 'default'):
                value = dh.default
        res[fieldname] = value
    if len(errors) > 0:
        del(res)
        raise HttpErrors(errors, title="Form validation error")
    return res
