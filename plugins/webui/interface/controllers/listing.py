from .base import get_response

def list_classes(request):
    # TODO Add the method to get the classes list
    template_vars = {'id': request.url_args[0]}

    return get_response('listing/list_classes.html')