## @package lodel.plugins.dummy_datasource Example of a datasource type plugin

# Here we use the Lodel Context Manager to expose the modules which are specific to the application
from lodel.validator.validator import Validator
from .datasource import DummyDatasource as Datasource

## @brief plugin's category
__plugin_type__ = 'datasource'
## @brief plugin's name (matching the package's name)
__plugin_name__ = "dummy_datasource"
## @brief plugin's version
__version__ = '0.0.1'
## @brief plugin's main entry module
__loader__ = 'main.py'
## @brief plugin's dependances
__plugin_deps__ = []

## @brief Plugin's configuration options and their corresponding validators
CONFSPEC = {
    'lodel2.datasource.dummy_datasource.*' : {
        'dummy': (  None,
                    Validator('dummy', none_is_valid=True))}
}


