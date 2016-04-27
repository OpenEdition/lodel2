from lodel.interface.web.controllers import *

urls = (
    (r'^$', index),
    (r'admin/?$', admin),
    (r'admin/(.+)$', admin),
    (r'test/(.+)$', test),
    (r'test/?$', test)
)