from lodel.utils.ini_files import ini_to_dict

## @brief Represents a Lodel Site
# @note This class could inherit from Blueprint
class LodelSite(object):
    
    def __init__(self, settings_file):
        self.settings_file = settings_file
    
    @property
    def settings(self):
        return ini_to_dict(self.settings_file)
    
    def config(self, state):
        lodelsite_settings = self.settings
        if lodelsite_settings:
            state.app.config['sites'][lodelsite_settings['Description']['shortname']] = lodelsite_settings
