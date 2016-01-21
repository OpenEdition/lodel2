# -*- coding: utf-8 -*-

from flask import Flask
from flask import request

import Router

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    url_elements = path.split('/')
    url_arguments = request.args
    return "%s" % url_elements


if __name__ == '__main__':
    app.run()