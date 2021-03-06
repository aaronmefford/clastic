# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from pytest import raises

from functools import wraps

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from clastic import Application
from clastic.decorators import clastic_decorator

from clastic.tests.common import hello_world, RequestProvidesName


def store_call_count(f):
    f.call_count = getattr(f, 'call_count', 0)

    @wraps(f)
    def g(*a, **kw):
        f.call_count += 1
        return f(*a, **kw)
    return g

cl_store_call_count = clastic_decorator(store_call_count)

hello_world_no = store_call_count(hello_world)
hello_world_ok = cl_store_call_count(hello_world)


def test_cl_decorated():
    req_provides_blank = RequestProvidesName()
    app = Application([('/', hello_world_ok)],
                      middlewares=[req_provides_blank])
    c = Client(app, BaseResponse)
    resp = c.get('/')
    assert resp.data == 'Hello, world!'
    resp = c.get('/?name=Kurt')
    assert resp.data == 'Hello, Kurt!'


def test_broken_decorated():
    req_provides_blank = RequestProvidesName()
    app = Application([('/', hello_world_no)],
                      middlewares=[req_provides_blank])
    c = Client(app, BaseResponse)
    resp = c.get('/')
    assert resp.data == 'Hello, world!'
    resp = c.get('/?name=Kurt')
    assert resp.data != 'Hello, Kurt!'


def test_undecoratable():
    with raises(TypeError):
        @clastic_decorator(store_call_count)
        def star_endpoint(**kwargs):
            return kwargs

        Application([('/', star_endpoint)])  # technically not reached
    return
