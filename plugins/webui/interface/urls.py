# -*- coding: utf-8 -*-
from .controllers import *

urls = (
    (r'^/?$', index),
    (r'^/admin/?$', admin),
    (r'^/admin/(.+)$', admin),
    (r'/test/(?P<id>.*)$', test),
    (r'^/test/?$', test),
    #(r'/show/(?P<id>.*)$', show_document),
    (r'^/list_classes', list_classes),
    (r'^/show_object/(.+)$', show_object),
    (r'^/show_object/?$', show_object),
    (r'^/show_class/(.+)$', show_class),
    (r'^/show_class/?$', show_class)
)
