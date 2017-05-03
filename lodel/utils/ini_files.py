from configparser import ConfigParser, MissingSectionHeaderError

## @brief Returns a dictionary from an ini file content
# @param ini_file_path str
# @return dict
# @throw MissingSectionHeaderError
# @todo Implement a better way to deal with this exception
def ini_to_dict(ini_file_path):
    result = {}
    try:
        config = ConfigParser()
        config.read(ini_file_path)
        result = config.__dict__['_sections'].copy()
    except MissingSectionHeaderError as e:
        pass
    
    return result
