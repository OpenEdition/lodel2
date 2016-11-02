# -*- coding: utf-8 -*-
from ...exceptions import *
from .base import get_response

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.leapi.exceptions': [],
    'lodel.logger': 'logger':
    'lodel.leapi.datahandlers.base_classes': ['MultipleRef']})

from ...client import WebUiClient
import leapi_dyncode as dyncode
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
    
    # If the form has been submitted
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
            raise HttpException(400, custom = "Bad classname given")

        leo_to_update = target_leo.get_from_uid(uid)
        
        errors = dict()
        for fieldname, value in request.form.items():
            #We want to drop 2 input named 'classname' and 'uid'
            if len(fieldname) > 12:
                #Other input names are : field_input_FIELDNAME
                #Extract the fieldname
                fieldname = fieldname[12:]
                try:
                    dh = leo_to_update.data_handler(fieldname)
                except NameError as e:
                    errors[fieldname] = e
                    continue
                #Multiple ref list preparation
                if issubclass(dh.__class__, MultipleRef):
                    value=[spl for spl in [
                           v.strip() for v in value.split(LIST_SEPARATOR)]
                        if len(spl) > 0]
                elif len(value.strip()) == 0:
                    value = None
                try:
                    leo_to_update.set_data(fieldname, value)
                except Exception as e:
                    errors[fieldname] = e
                    continue
        if len(errors) > 0:
            custom_msg = '<h1>Errors in datas</h1><ul>'
            for fname, error in errors.items():
                custom_msg += '<li>%s : %s</li>' % (
                    fname, error)
            custom_msg += '</ul>'
            raise HttpException(400, custom = custom_msg)
        leo_to_update.update()

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
    classname = None
     # If the form has been submitted
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
            # The classname is handled by the datasource, we are not allowed to modify it
            # both are hidden in the form, to identify the object here
            if in_put != 'classname' and in_value != '':
                dhl = target_leo.data_handler(in_put[12:])
                if dhl.is_reference() and in_value != '' and not dhl.is_singlereference():
                    logger.info(in_value)
                    in_value.replace(" ","")
                    in_value=in_value.split(',')
                    in_value=list(in_value)
                fields[in_put[12:]] = in_value
            if in_value == '':
                fields[in_put[12:]] = None             

        # Insertion in the database of the values corresponding to a new object
        new_uid = target_leo.insert(fields)
        
        # reurn to the form with a confirmation or error message
        if not new_uid is None:
            msg = 'Successfull creation';
        else:
            msg = 'Oops something wrong happened...object not saved'
        return get_response('admin/admin_create.html', target=target_leo, msg = msg)
    
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


