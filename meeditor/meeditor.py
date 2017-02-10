
import sys
from os import path

sys.path.insert(0, path.abspath('..'))

from flask import Flask
from flask import render_template, redirect
from flask import request
from flask import jsonify

from lodel.context import LodelContext
LodelContext.init()

from lodel.settings.settings import Settings as settings
settings('globconf.d')
from lodel.settings import Settings

from lodel.editorial_model.components import *
from lodel.editorial_model.exceptions import *
from lodel.editorial_model.model import EditorialModel

em = EditorialModel('LodelSites', 'LodelSites editorial model')


import settings

app = Flask(__name__)

# Lodel EditorialModel initialization

@app.route('/')
def meeditor(methods=['GET']):
    return jsonify({})

if __name__ == '__main__':
    app.config.update(JSONIFY_PRETTYPRINT_REGULAR=False)
    app.run(host=settings.HOST_NAME)
