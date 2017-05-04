import os

from flask.templating import render_template_string
from flask_script import Command, Option


class LodelCommand(Command):
    
    option_list = (
        Option('--name', '-n', dest='name'),
    )

    ## @brief Creates a new lodel site
    # @param name str
    # @todo dynamically define the lodelsites folder
    def run(self, name):
        os.mkdir("sites/%s" % name)
        os.mkdir("sites/%s/templates" % name)
        os.mkdir("sites/%s/templates/%s" % (name, name))
    
        with open("sites/%s/__init__.py" % name, 'w') as init_file:
            init_file.write(render_template_string("""from flask import Blueprint
from lodel.lodelsites.lodelsite import LodelSite

import os

settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")

lodelsite = LodelSite(settings_file)
lodelsite_{{shortname}} = Blueprint(
    lodelsite.settings['Description']['shortname'],
    __name__,
    template_folder=lodelsite.settings['Description']['templates_folder'],
    url_prefix="/{{ shortname }}")
lodelsite_{{shortname}}.record_once(lodelsite.config)

from .views import *""", **{'shortname':name}))
    
        with open("sites/%s/views.py" % name, "w") as views_file:
            views_file.write(render_template_string("""from flask import render_template, abort, current_app
from jinja2 import TemplateNotFound

from . import lodelsite_{{shortname}}

@lodelsite_{{shortname}}.route('/', defaults={'page':'index'})
@lodelsite_{{shortname}}.route('/{{ "<page>" | safe }}')
def show(page):
    try:
        return render_template("{{ shortname }}/%s.html" % page, **{'settings': current_app.config['sites']['{{shortname}}']})
    except TemplateNotFound:
        abort(404)""", **{'shortname':name}))

        with open("sites/%s/templates/%s/index.html" % (name, name), "w") as index_tpl:
            index_tpl.write("<strong>{{ settings['Description']['name'] }}</strong>")
    
        with open("sites/%s/settings.ini" % name, "w") as settings_file:
            settings_file.write(render_template_string("""[Description]
name={{ name }}
shortname={{ shortname }}
templates_folder=templates""", **{'name': name, 'shortname': name}))
    
        print("site %s created successfully" % name)
