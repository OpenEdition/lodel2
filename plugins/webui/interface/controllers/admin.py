from .base import get_response

def index_admin(request):
    return get_response('admin/admin.html')

def admin(request):
    return get_response('admin/admin.html')


