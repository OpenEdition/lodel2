##
#@note in itself thos method should be implemented as custom methods
#for Lodelsite leobject. The current state of the project do not allow
#to do this easily. So you will found them here for the moment....

import os.path
from lodel import buildconf #safe even outside any context

from lodel.context import LodelContext


##@brief Update the leapi_dyncode.py file for a given site
#
#Follows expectation of LodelContext :
#The leapi_dyncode.py file will be stored in site's context dir
#@param site_name str : site shortname
#@param em_groups list : list of em groups to enable in the dyncode
#@return Nothing
def update_dyncode(site_name, em_groups):
    _, ctx_path = LodelContext.lodelsites_paths()
    dyncode_path = os.path.join(os.path.join(ctx_path, site_name),
            buildconf.MULTISITE_DYNCODE_MODULENAME+'.py')
    LodelContext.expose_modules(globals(), {
            'lodel.logger': 'logger',
            'lodel.settings': ['Settings'],
            'lodel.editorial_model.model': ['EditorialModel'],
            'lodel.leapi.lefactory': 'lefactory'})

    EditorialModel._override_settings(False, em_groups)
    model = EditorialModel.load(
        Settings.lodelsites.sites_emtranslator,
        filename = Settings.lodelsites.sites_emfile)
    logger.info('EditorialModel loaded for handled site %s' % site_name)
    dyncode = lefactory.dyncode_from_em(model)
    with open(dyncode_path, 'w+') as dfp:
        dfp.write(dyncode)
    EditorialModel._override_settings() #Restoring safe values
    logger.info('Dyncode generated for handled site %s' % site_name)
    logger.debug('Dyncode for %s contains those groups : %s' % (
        site_name, em_groups))


