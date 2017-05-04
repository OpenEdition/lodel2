from flask_script import Manager

from lodel_app import lodel_app
from management.utils import register_commands

manager = Manager(lodel_app)
register_commands(manager)


if __name__ == "__main__":
    manager.run()