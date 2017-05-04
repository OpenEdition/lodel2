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


__plugin_type__ = 'datasource'
__plugin_name__ = 'mongodb_datasource'
__version__ = '0.0.1'
__plugin_type__ = 'datasource'

__loader__ = "main.py"
__confspec__ = "confspec.py"

__author__ = "Lodel2 dev team"
__fullname__ = "MongoDB plugin"


## @brief Activates the plugin
#
# @note This function can contain specific actions (like checks, etc ...) in 
#  order to activate the plugin.
#
# @return bool|str : True if all the checks are OK, an error message if not
def _activate():
    from lodel import buildconf  # NOTE : this one do not have to pass through the context
    return buildconf.PYMONGO

#
#   Doxygen comments
#

## @defgroup plugin_mongodb_datasource MongoDB datasource plugin
# @brief Doc about mongodb datasource

## @page plugin_mongodb_backref_complexity Reflexion on back reference complexity
# @ingroup plugin_mongodb_bref_op
#
# There is a huge performance issue in the way we implemented references and 
# back references for mongodb datasource :
#
# For each write action (update, delete or insert) we HAVE TO run a select
# on all concerned LeObject instances. Those methods' headers look like
# <pre>def write_action(target_cls, filters, [datas])</pre>.
#
# We have no idea if all the modified objects are of the target class (they
# can be of any target's child classes). So that means we have no idea of the
# @ref base_classes.Reference "References" that will be modified by the action.
#
# Another problem is that when we run an update or a delete we have no idea
# of the values that will be updated or deleted (we do not have the concerned
# instances datas). As a result we cannot replace or delete the concerned
# back references.
#
# In term of complexity the number of DB query looks like :
# <pre>
# With n the number of instances to modify : 
#   queryO(n) ~=  2n ( n * select + n * update )
# </pre>
#
# But it can go really bad, really fast if we take in consideration that
# query's can be done on mixed classes or abstract classes. With :
# - n : the number of LeObect child classes represented by the abstract class
# - m : the number of LeObject child classes for each n
# - o : the number of concerned back_reference classes for each m
#
# <pre>queryO(n,m,o) ~=  n + (n*m) + (n*m*o) => n + n*m select and n*m*o updates</pre>
#
# All of this is really sad especially as the update and the delete will be
# run on LeObject instances....
#
