# -*- coding: utf-8 -*-
from .controllers import *

urls = (
    (r'^/?$', index),
    (r'^/admin/?$', admin),
    (r'^/admin/create$', admin_create),
    (r'^/admin/update$', admin_update),
    (r'^/admin/classes_admin', admin_classes),
    (r'^/admin/object_create', create_object),
    (r'^/admin/class_admin$', admin_class),
    (r'/test/(?P<id>.*)$', test),
    (r'^/test/?$', test),
    (r'^/list_classes', list_classes),
    (r'^/list_classes?$', list_classes),
    (r'^/show_object?$', show_object),
    (r'^/show_class?$', show_class),
    (r'^/signin', signin),
    (r'^/signout', signout)
)
