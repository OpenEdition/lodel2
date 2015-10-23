#-*- coding: utf-8 -*-

## @brief Decorator to have methods with the same name callable from Class or from Instance
#
# Usage example :
# @code{.py}
#   class A(object):
#       @classinstancemethod
#       def foo(self, a, b):
#           print("foo() instance call", a ,b)
#       
#       @foo.classmethod
#       def foo(self):
#           print("foo() class call")
#
#       @classinstancemethod
#       def bar(obj):
#           if obj == A:
#               print("bar() class call")
#           else:
#               print("bar() instance call")
#
# a=A()
# A.foo() #foo() class call
# a.foo(1,2) #foo() instance call 1 2
# A.bar() #bar() class call
# a.bar() #bar() instance call
# @endcode
class classinstancemethod(object):
    def __init__(self, func):
        self._func = func
        self._classmethod = None

    def classmethod(self, func):
        self._classmethod = func

    def __get__(self, instance, cls):
        if instance is None:
            if self._classmethod is None:
                return self._func.__get__(cls, cls)
            else:
                return self._classmethod.__get__(instance, cls)
        else:
            return self._func.__get__(instance, cls)
