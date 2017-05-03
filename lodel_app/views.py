from . import lodel_app

@lodel_app.route("/")
def hello_world():
    return "Hello World"