# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from pytest import raises

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from clastic.application import Application

from clastic.tests.common import hello_world, DummyMiddleware, RequestProvidesName


def test_create_empty_application():
    app = Application()
    return app


def test_create_hw_application():
    route = ('/', hello_world)
    app = Application([route])
    assert app.routes
    assert callable(app.routes[0]._execute)
    assert app.routes[0]._bound_apps[0] is app


def test_single_mw_basic():
    dumdum = DummyMiddleware()
    app = Application([('/', hello_world)],
                      resources={},
                      middlewares=[dumdum])
    assert dumdum in app.middlewares
    assert dumdum in app.routes[0]._middlewares

    resp = Client(app, BaseResponse).get('/')
    assert resp.status_code == 200


def test_duplicate_noarg_mw():
    for mw_count in range(0, 100, 20):
        mw = [DummyMiddleware() for i in range(mw_count)]
        app = Application([('/', hello_world)],
                          middlewares=mw)
        assert app
        assert len(app.routes[0]._middlewares) == mw_count

        resp = Client(app, BaseResponse).get('/')
        assert resp.status_code == 200
    return


def test_duplicate_arg_mw():
    with raises(NameError):
        req_provides1 = RequestProvidesName('Rajkumar')
        req_provides2 = RequestProvidesName('Jimmy John')
        Application([('/', hello_world)],
                    middlewares=[req_provides1,
                                 req_provides2])
    return


def test_resource_builtin_conflict():
    with raises(NameError):
        Application(resources={'next': lambda: None})


def test_subapplication_basic():
    dum1 = DummyMiddleware()
    dum2 = DummyMiddleware()
    no_name_app = Application([('/', hello_world)],
                              middlewares=[dum1])
    name_app = Application([('/', hello_world),
                            ('/foo', hello_world)],
                           resources={'name': 'Rajkumar'},
                           middlewares=[dum1])
    app = Application([('/', no_name_app),
                       ('/beta/', name_app)],
                      resources={'name': 'Kurt'},
                      middlewares=[dum2])

    assert len(app.routes) == 3

    merged_name_app_patts = [r.pattern for r in app.routes
                             if r.pattern.startswith('/beta')]
    name_app_patts = [r.pattern for r in name_app.routes]

    def check_patts(app_patts, subapp_patts):
        return all(a.endswith(s) for a, s in zip(app_patts, subapp_patts))

    # should be the same order as name_app
    assert len(merged_name_app_patts) == len(name_app_patts)
    assert check_patts(merged_name_app_patts, name_app_patts)

    assert len(set([r.pattern for r in app.routes])) == 3
    assert len(app.routes[0]._middlewares) == 1  # middleware merging

    resp = Client(no_name_app, BaseResponse).get('/')
    assert resp.data == 'Hello, world!'
    resp = Client(name_app, BaseResponse).get('/')
    assert resp.data == 'Hello, Rajkumar!'
    resp = Client(app, BaseResponse).get('/')
    assert resp.data == 'Hello, Kurt!'
    resp = Client(app, BaseResponse).get('/beta/')
    assert resp.data == 'Hello, Kurt!'
    resp = Client(app, BaseResponse).get('/beta/foo')
    assert resp.data == 'Hello, Kurt!'
    resp = Client(app, BaseResponse).get('/larp4lyfe/')
    assert resp.status_code == 404
