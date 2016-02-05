#-*- coding: utf-8 -*-
import unittest
import unittest.mock
from unittest.mock import call, patch

from . import transwrap
from .transwrap import DefaultCallCatcher

class DummyClass(object):
    cls_attr = "Woot"

    def __init__(self, prop = None, *args, **kwargs):
        self._prop = self.clsfun(prop)

    @classmethod
    def clsfun(cls, a=None):
        return 'foo' if a is None else a

    @staticmethod
    def statfun(*args):
        return args

    def fun(self, foo=''):
        return None if len(foo) == 0 else foo

    def __str__(self):
        return self.fun('wow')

    def __repr__(self):
        return 'its me : %s' %self._prop

    def __int__(self):
        return 0

    def __add__(self, other): return other
    def __len__(self): return -1

class DummyCatcher(DefaultCallCatcher):
    @classmethod
    def attr_get(self, obj, attr_name):
        return super().attr_get(obj, attr_name)

    @classmethod
    def method_call(self, obj, method, args, kwargs):
        return super().method_call(obj, method, args, kwargs)

class TransWrapTestCase(unittest.TestCase):
    """ TestCase for user defined class mock """

    def setUp(self):
        DummyCatcher.attr_get = unittest.mock.Mock()
        DummyCatcher.method_call = unittest.mock.Mock()
        self.wrap = transwrap.get_wrap(DummyClass, DummyCatcher)
        DummyCatcher.method_call.reset_mock()
        DummyCatcher.attr_get.reset_mock()

    def test_init(self):
        """ Testing constructor """
        tmp = self.wrap()
        expt_calls = [
            call(tmp, tmp.__setattr__, ('_prop', None), dict()),
            call(DummyClass, DummyClass, tuple(), dict()),
        ]
        DummyCatcher.method_call.asser_has_calls(expt_calls)

    def test_args(self):
        """ Testing positional arguments catch """
        args = [tuple(), (42,), ("hello",), (1,2,3,[4,5,6])]
        for arg in args:
            tmp = self.wrap(*arg)
            setattr_arg = None if len(arg) == 0 else arg[0]
            expt_calls = [
                call(tmp, tmp.__setattr__, ('_prop', setattr_arg), dict()),
                call(DummyClass, DummyClass, arg, dict()),
            ]
            DummyCatcher.method_call.asser_has_calls(expt_calls)
            DummyCatcher.method_call.reset_mock()

    def test_kwarg(self):
        """ Testing kwargs arguments catch"""
        kwargs = [ dict(), {'foo':'bar'}, {'answer': 42, 'question': None}, {'prop': 42, 'foobar': None} ]
        for kwarg in kwargs:
            tmp = self.wrap(**kwarg)
            setattr_arg = kwarg['prop'] if 'prop' in kwarg == 0 else None
            expt_calls = [
                call(tmp, tmp.__setattr__, ('_prop', setattr_arg), dict()),
                call(DummyClass, DummyClass, kwarg, dict()),
            ]
            DummyCatcher.method_call.asser_has_calls(expt_calls)
            DummyCatcher.method_call.reset_mock()

    def test_argkwarg(self):
        """ Testing positional and keyword arguments catch"""
        arglist = [
            (
                tuple(),
                dict()
            ),
            (
                (42,),
                dict()
            ),
            (
                tuple(),
                {'foo': 'bar'}
            ),
            (
                (42,1337,51),
                {'42':42, '1337':1337, '51':[51,52,53]}
            )
        ]
        for args, kwargs in arglist:
            tmp = self.wrap(*args, **kwargs)
            if 'prop' in kwargs:
                setattr_arg = kwargs['prop']
            elif len(args) > 0:
                setattr_arg = args[0]
            else:
                setattr_arg = None
            expt_calls = [
                call(tmp, tmp.__setattr__, ('_prop', setattr_arg), dict()),
                call(DummyClass, DummyClass, args, kwargs),
            ]
            DummyCatcher.method_call.asser_has_calls(expt_calls)
            DummyCatcher.method_call.reset_mock()

    def test_classmethod(self):
        """ Testing classmethod wrapping"""
        args = [ tuple(), (42,), ("hello",)]
        for arg in args:
            self.wrap.clsfun()
            DummyCatcher.method_call.assert_called_once_with(DummyClass, DummyClass.clsfun, tuple(), dict())
            DummyCatcher.method_call.reset_mock()

    def test_instance_attr(self):
        """ Testing instance implicit attribute get wrapping """
        dumm = self.wrap()
        DummyCatcher.method_call.reset_mock()
        DummyCatcher.attr_get.reset_mock()
        # reset mock calls after instanciation
        foo = dumm._prop
        DummyCatcher.attr_get.assert_called_once_with(dumm, '_prop')
        DummyCatcher.method_call.assert_not_called()

    #@unittest.skip("We need a different mocking to test this")
    def test_instance_setattr(self):
        """ Testing instance implicit attribute set wrapping """
        dumm = self.wrap()
        # fetching dumm._instance
        instance = object.__getattribute__(dumm, '_instance')
        # reset mock calls after instanciation
        DummyCatcher.method_call.reset_mock()
        DummyCatcher.attr_get.reset_mock()

        dumm._prop = 42
        DummyCatcher.method_call.assert_called_once_with(instance, instance.__setattr__ , ('_prop',42), dict())
        DummyCatcher.attr_get.assert_not_called()

    def test_class_getattr(self):
        """ Testing class implicit attribute get wrapping"""
        foo = self.wrap.cls_attr
        DummyCatcher.attr_get.assert_called_once_with(self.wrap, 'cls_attr')
        DummyCatcher.method_call.assert_not_called()

    def test_class_setattr(self):
        """ Testing class implicit attribute set wrapping"""
        self.wrap.cls_attr = 42
        DummyCatcher.method_call.assert_called_once_with(DummyClass.__class__, DummyClass.__class__.__setattr__, (DummyClass,'cls_attr', 42), dict())
        DummyCatcher.attr_get.assert_not_called()


class AnotherMockTestCase(unittest.TestCase):

    def test_implicit_magic_instance(self):
        """ Testing implicit magic method call on instances """
        wrapper = transwrap.get_wrap(DummyClass, DummyCatcher)
        dumm = wrapper()

        # fetching dumm._instance
        instance = object.__getattribute__(dumm, '_instance')
        
        # repr
        with patch.object(DummyCatcher, 'method_call', return_value = None) as momock:
            try: repr(dumm)
            except TypeError as e: pass #Raised because repr returned a mock class :^°
            momock.assert_called_once_with(instance, instance.__repr__, (), dict())
        # str
        with patch.object(DummyCatcher, 'method_call', return_value = None) as momock:
            try: str(dumm)
            except TypeError as e: pass
            momock.assert_called_once_with(instance, instance.__str__, (), dict())
        # int
        with patch.object(DummyCatcher, 'method_call', return_value = None) as momock:
            try: int(dumm)
            except TypeError as e: pass
            momock.assert_called_once_with(instance, instance.__int__, (), dict())
        # hash
        with patch.object(DummyCatcher, 'method_call', return_value = None) as momock:
            try: hash(dumm)
            except TypeError as e: pass
            momock.assert_called_once_with(instance, instance.__hash__, (), dict())
        # len
        with patch.object(DummyCatcher, 'method_call', return_value = None) as momock:
            try: len(dumm)
            except TypeError as e: pass
            momock.assert_called_once_with(instance, instance.__len__, (), dict())
        # add
        with patch.object(DummyCatcher, 'method_call', return_value = None) as momock:
            try: foo = dumm + 2
            except TypeError as e: pass
            momock.assert_called_once_with(instance, instance.__add__, (2,), dict())
        # str
        with patch.object(DummyCatcher, 'method_call', return_value = None) as momock:
            try: str(dumm)
            except TypeError as e: pass
            momock.assert_called_once_with(instance, instance.__str__, (), dict())
    ## @todo classmethod magics
    @unittest.skip("TODO")
    def test_implicit_magic_class(self):
        pass
