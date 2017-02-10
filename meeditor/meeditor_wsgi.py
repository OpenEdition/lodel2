
from meeditor import app

if __name__ == '__main__':
    app.config.update(JSONIFY_PRETTYPRINT_REGULAR=False)
    app.run()
