#-*- coding: utf-8 -*-

from Lodel.plugins import leapi_method, leapi_classmethod

@leapi_method('LeObject', 'test_method')
def a_name(self, arg1):
    print("Hello from %s. arg1 = %s" % (self, arg1))

@leapi_classmethod('LeObject', 'test_classmethod')
def another_name(cls):
    print("I'm a super class method from class %s" % cls)
