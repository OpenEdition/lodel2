from . import lodel_app
from flask.globals import session

@lodel_app.before_request
def make_session_permanent():
    session.permanent = True