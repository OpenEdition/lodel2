##@brief Contains some constants in order to check that a LeObject child
#is compatible with the datasource
#
#@note isolated in order to be usable by __init__.py and main.py

LEO_NAME = 'Lodelsite'
MANDATORY_FIELDNAMES = [ 'shortname', 'extensions', 'groups' ]

##@brief Checks that given emcomponent is compatible with datasource
#behavior
#@warning 100% hardcoded checks on leo name fieldnames & types
#@param emcomp LeObject subclass (or instance)
#@return a tuple (bool, reason_str)
def check(leo):
    if hasattr(leo, '__class__'):
        leo = leo.__class__
    if leo.__name__ != LEO_NAME:
        return (False, 'bad name')
    missings = MANDATORY_FIELDNAMES - set(leo.fieldnames())
    if len(missings) > 0:
        return (False, 'missing fields : ' + (', '.join(missings)))
    return (True, 'ok')
