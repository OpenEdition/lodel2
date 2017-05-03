from flask import Flask
import os

from lodel.lodelsites.utils import register_lodelsites
from lodel.utils.ini_files import ini_to_dict


lodel_app = Flask(__name__)
lodel_app.config['DEBUG'] = True
lodel_app.config['sites'] = {}
lodel_app.config.update(ini_to_dict(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')))

# Lodelsites
register_lodelsites(lodel_app)

# Main views
from .views import *
