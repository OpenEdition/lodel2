##@brief Plugin designed to handle FS site creation
#
#This plugin has a strong coupling with the multisite EM. It is 
#designed to handle only 1 EmClass : Lodelsite .
#This class must have some mandatory fields :
# - shortname
# - extensions : list of loaded plugins
# - em_groups : selected Em Group from base Em
#
# Every other fields are ignored by this datasource and forwarded to
#childs datasource.

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator'],
    'lodel.logger': 'logger'})
from .specs import check

__plugin_type__ = 'datasource'
__plugin_name__ = "lodelsite_datasource"
__version__ = '0.0.1'
__loader__ = 'main.py'
__plugin_deps__ = []

CONFSPEC = {
    'lodel2.datasource.lodelsite_datasource.*' : {
        'db_datasource': (  None,
            Validator('string')),
        'db_datasource_ro': (None,
            Validator('string', none_is_valid = True)),
    }
}


##@brief Hardcoded checks that try to know if the EM fits the requierements
def _activate():
    LodelContext.expose_dyncode(globals())
    if 'Lodelsite' not in leapi_dyncode.dynclasses_dict:
        logger.fatal('Unable to activate lodelsite_datasource. Expected a \
Lodelsite leapi object')
        return False #or raise ?
    LodelSite = leapi_dyncode.dynclasses_dict['Lodelsite']
    res, reason = check(LodelSite)
    if not res:
        logger.fatal('The lodelsite EmClass has some missins mandatory \
fields : '+reason)
    return res
            

