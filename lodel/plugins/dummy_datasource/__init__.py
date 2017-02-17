from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})
from .datasource import DummyDatasource as Datasource

__plugin_type__ = 'datasource'
__plugin_name__ = "dummy_datasource"
__version__ = '0.0.1'
__loader__ = 'main.py'
__plugin_deps__ = []

CONFSPEC = {
    'lodel2.datasource.dummy_datasource.*' : {
        'dummy': (  None,
                    Validator('dummy'))}
}


