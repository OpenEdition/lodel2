# CLI Commands called by the lodeladmin module

from lodeladmin import manager

@manager.command
def hello():
    print("Hello, World!")
