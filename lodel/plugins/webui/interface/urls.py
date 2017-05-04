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


from .controllers import *

urls = (
    (r'^/?$', index),
    (r'^/admin/?$', admin),
    (r'^/admin/create$', admin_create),
    (r'^/admin/update$', admin_update),
    (r'^/admin/delete$', admin_delete),
    (r'^/admin/classes_admin', admin_classes),
    (r'^/admin/object_create', create_object),
    (r'^/admin/object_delete', delete_object),
    (r'^/admin/class_admin$', admin_class),
    (r'^/admin/class_delete$', delete_in_class),
    (r'^/admin/search$', search_object),
    (r'/test/(?P<id>.*)$', test),
    (r'^/test/?$', test),
    (r'^/list_classes', list_classes),
    (r'^/list_classes?$', list_classes),
    (r'^/collections', collections),
    (r'^/collections?$', collections),
    (r'^/issue?$', issue),
    (r'^/show_object?$', show_object),
    (r'^/show_object_detailled?$', show_object_detailled),
    (r'^/show_class?$', show_class),
    (r'^/signin', signin),
    (r'^/signout', signout)
)
