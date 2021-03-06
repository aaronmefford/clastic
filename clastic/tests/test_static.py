# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os

from werkzeug.test import Client
from clastic import Application, StaticApplication, Response, StaticFileRoute

_CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def test_basic_static_serve():
    static_app = StaticApplication(_CUR_DIR)
    app = Application([('/static/', static_app)])

    c = Client(app, Response)
    resp = c.get('/static/test_static.py')
    assert resp.mimetype == 'text/x-python'
    resp = c.get('/static/does_not_exist.txt')
    assert resp.status_code == 404
    resp = c.get('/static/../core.py')
    assert resp.status_code == 403
    resp = c.get('/static/_ashes_tmpls/basic_template.html')
    assert resp.status_code == 200
    resp = c.get('/static/_ashes_tmpls/../../core.py')
    assert resp.status_code == 403
    resp = c.get('/static//etc/hosts')
    assert resp.status_code == 403


def test_basic_static_route():
    static_app = Application([StaticFileRoute('/source_code',
                                              _CUR_DIR + '/test_static.py')])

    c = Client(static_app, Response)
    resp = c.get('/source_code')
    assert resp.mimetype == 'text/x-python'
    assert resp.status_code == 200
