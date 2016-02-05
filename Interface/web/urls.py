from .controllers import *


urls = (
    (r'^$', index),
    (r'admin/?$', admin),
    (r'admin/(.+)$', admin)
)
