from flask import Flask
import os

from lodel.lodelsites.utils import register_lodelsites
from lodel.utils.ini_files import ini_to_dict
from lodel.session.lodel_filesystem_session.lodel_filesystem_session_interface import LodelFileSystemSessionInterface
from lodel.session.lodel_ram_session.lodel_ram_session_interface import LodelRamSessionInterface


lodel_app = Flask(__name__)
lodel_app.config['DEBUG'] = True
lodel_app.config['sites'] = {}
lodel_app.config.update(ini_to_dict(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')))

lodel_app.session_cookie_name = lodel_app.config['lodel.sessions']['session_cookie_name']
lodel_app.permanent_session_lifetime = int(lodel_app.config['lodel.sessions']['session_lifetime'])
lodel_app.session_interface = LodelRamSessionInterface()  # LodelFileSystemSessionInterface(lodel_app.config['lodel.filesystem_sessions']['path'])

# Main Hooks
from .hooks import *

# Lodelsites
register_lodelsites(lodel_app)

# Main views
from .views import *
