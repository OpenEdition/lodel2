import os

## @brief Registers a lodelsite
#
# Each lodelsite is a Flask Blueprint.
#
# @param lodelapp Flask : application in which the lodelsite will be registered
# @param sitepath str
# @todo Use the main settings to get the lodelsites_main_module value
def register_lodelsites(lodelapp):
    lodelsites_main_module = 'sites'
    lodelsites_main_module_path = os.path.abspath(lodelsites_main_module)
    
    sitenames = os.listdir(lodelsites_main_module_path)
    for sitename in sitenames:
        # We check if the found item is a python package
        if os.path.isfile('%s/%s/__init__.py' % (lodelsites_main_module_path, sitename)):
            module = __import__('%s.%s' % (lodelsites_main_module, sitename), globals(), locals(), [sitename], 0)
            bp = getattr(module, 'lodelsite_%s' % sitename)
            lodelapp.register_blueprint(bp)
