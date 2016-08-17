from lodel.settings.validator import SettingValidator
from .datasource import DummyDatasource as Datasource

__plugin_name__ = "dummy_datasource"
__version__ = '0.0.1'
__loader__ = 'main.py'
__plugin_deps__ = []

CONFSPEC = {
    'lodel2.datasource.dummy_datasource.*' : {
        'dummy': (  None,
                    SettingValidator('dummy'))}
}

##@page lodel2_datasources Lodel2 datasources
#
#@par lodel2_datasources_intro Intro
# A single lodel2 website can interact with multiple datasources. This page
# aims to describe configuration & organisation of datasources in lodel2.
# Each object is attached to a datasource. This association is done in the
# editorial model, the datasource is identified by a name.
#
#@par Datasources declaration
# To define a datasource you have to write something like this in confs file :
#<pre>
#[lodel2.datasources.DATASOURCE_NAME]
#identifier = DATASOURCE_FAMILY.SOURCE_NAME
#</pre>
# See below for DATASOURCE_FAMILY & SOURCE_NAME
#
#@par Datasources plugins
# Each datasource family is a plugin. For example mysql or a mongodb plugins.
# Here is the CONFSPEC variable templates for datasources plugins
#<pre>
#CONFSPEC = {
#                'lodel2.datasource.example.*' : {
#                    'conf1' : VALIDATOR_OPTS,
#                    'conf2' : VALIDATOR_OPTS,
#                    ...
#                }
#}
#</pre>
#MySQL example
#<pre>
#CONFSPEC = {
#                'lodel2.datasource.mysql.*' : {
#                    'host': (   'localhost',
#                                SettingValidator('host')),
#                    'db_name': (    'lodel',
#                                    SettingValidator('string')),
#                    'username': (   None,
#                                    SettingValidator('string')),
#                    'password': (   None,
#                                    SettingValidator('string')),
#                }
#}
#</pre>
#
#@par Configuration example
#<pre>
# [lodel2.datasources.main]
# identifier = mysql.Core
# [lodel2.datasources.revues_write]
# identifier = mysql.Revues
# [lodel2.datasources.revues_read]
# identifier = mysql.Revues
# [lodel2.datasources.annuaire_persons]
# identifier = persons_web_api.example
# ;
# ; Then, in the editorial model you are able to use "main", "revues_write", 
# ; etc as datasource
# ;
# ; Here comes the datasources declarations
# [lodel2.datasource.mysql.Core]
# host = db.core.labocleo.org
# db_name = core
# username = foo
# password = bar
# ;
# [lodel2.datasource.mysql.Revues]
# host = revues.org
# db_name = RO
# username = foo
# password = bar
# ;
# [lodel2.datasource.persons_web_api.example]
# host = foo.bar
# username = cleo
#</pre>
