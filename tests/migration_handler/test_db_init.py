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


from lodel import buildconf

if not buildconf.PYMONGO:
    import warnings
    warnings.warn("Skipping tests about mongodb datasource. Pymongo not installed")
else:
    import unittest
    from plugins.mongodb_datasource.migration_handler import *
    class MongoDbMigrationHandlerTestCase(unittest.TestCase):

        def test_check_connection_args(self):
            empty_connection_args = {}
            with self.assertRaises(TypeError):
                MigrationHandler(empty_connection_args)

            bad_connection_args_dicts = [
                {'host': 'localhost', 'port': 20030},
                {'host': 'localhost', 'port': 28015},
                {'host': 'localhost', 'port': 28015, 'login':'lodel', 'password': 'lap'}
            ]
            for bad_connection_args_dict in bad_connection_args_dicts:
                with self.assertRaises(TypeError):
                    MigrationHandler(bad_connection_args_dict)

        ## @todo pass the connection arguments in the settings
        @unittest.skip
        def test_init_db(self):
            correct_connection_args = {'host': 'localhost', 'port': 28015, 'username': 'lodel_admin', 'password': 'lapwd', 'db_name': 'lodel'}
            migration_handler = MigrationHandler(correct_connection_args)
            migration_handler.init_db()
