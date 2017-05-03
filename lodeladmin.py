from flask_script import Manager
from lodel_app import lodel_app

manager = Manager(lodel_app)

from management import *

if __name__ == "__main__":
    manager.run()