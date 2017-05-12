from . import lodel_app
from flask.templating import render_template
from flask import request

# BASE
@lodel_app.route('/')
def index():
    return render_template('index/index.html')

@lodel_app.route('/notfound')
def not_found():
    return render_template('errors/404.html'), 404

@lodel_app.route('/test')
def test():
    if request.url_args.get('id', None) is None:
        id_arg = None
    else:
        id_arg = request.url_args['id']
    
    return render_template('test.html', **{'id':id_arg, 'params': request.GET})

# ADMIN
@lodel_app.route('/admin')
def index_admin():
    return render_template('admin/admin.html')

