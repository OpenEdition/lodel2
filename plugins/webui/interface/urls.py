from .controllers import *

urls = (
    (r'^$', index),
    (r'admin/?$', admin),
    (r'admin/(.+)$', admin),
    (r'test/(.+)$', test),
    (r'test/?$', test),
    (r'show/(?P<id>.*)$', show_document),
    (r'list_classes/(.+)$', list_classes),
    (r'list_classes/?$', list_classes),
)
