# -*- coding: utf-8 -*-

from flask import Flask
from flask import request

import Router

app = Flask(__name__)


@app.route('/', defaults={'path':''})
@app.route('/<path:path>')
def index(path):
    return "%s" % path


if __name__ == '__main__':
    app.run()