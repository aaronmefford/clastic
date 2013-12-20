# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from clastic import (Application,
                     default_response,
                     GetParamMiddleware)

from clastic.middleware import SimpleContextProcessor
from clastic.middleware.cookie import SignedCookieMiddleware
from clastic.tests.common import cookie_hello_world

from pprint import pformat
import time
import sys


def see_modules(start_time, module_list, name=None):
    name = name or 'world'
    return (('Hello, %s, this app started at %s and has the following'
             ' modules available to it: \n\n%s')
            % (name, start_time, pformat(sorted(module_list))))


def debug(request, _application, _route):
    import pdb;pdb.set_trace()
    return {}


def create_decked_out_app():
    resources = {'start_time': time.time(),
                 'module_list': sys.modules.keys()}
    middlewares = [GetParamMiddleware(['name', 'date', 'session_id']),
                   SignedCookieMiddleware(),
                   SimpleContextProcessor('name')]
    routes = [('/', cookie_hello_world, default_response),
              ('/debug', debug, default_response),
              ('/modules/', see_modules, default_response)]
    return Application(routes, resources, None, middlewares)


if __name__ == '__main__':
    create_decked_out_app().serve()
