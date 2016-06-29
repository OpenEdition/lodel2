from .base import get_response
import leapi_dyncode as dyncode
def list_classes(request):
    # TODO Add the method to get the classes list
    template_vars = {'my_classes': dyncode.dynclasses}
    return get_response('listing/list_classes.html', tpl_vars=template_vars)