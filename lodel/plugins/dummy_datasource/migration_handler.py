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


## @package lodel.plugins.dummy_datasource.migration_handler Migration handler of the datasource plugin. 
#
# The migration handler is here to report the changes made in the editorial model to the data source. 
# 
# For a database, it could be the creation/deletion of tables, the addition/deletion/change of certain columns, etc...
#
# We also have here the datasource initialization process, for the first use of it. The migration handler will then
# use the editorial model to generate the corresponding data storage. 

## @brief Abtract class for migration handlers
class DummyMigrationHandler(object):

    ## @brief Create a new migration handler given DB connection options
    def __init__(self, *args, **kwargs):
        pass
    
    ## @brief DB initialisation
    # @param emclass_list list : list of EmClasses concerned by this MH
    def init_db(self, emclass_list):
        pass
    
    ## @brief register a change in the editorial model
    # @param model EditorialModel
    # @param uid
    # @param initial_state
    # @param new_state
    # @todo redefine
    def register_change(self, model, uid, initial_state, new_state):
        pass

    ##
    # @param em EditorialModel
    # @param state_hash str
    # @todo redefine
    def register_model_state(self, em, state_hash):
        pass
    
