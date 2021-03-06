# -*- coding: utf-8 -*-

import os
import json
import time

from werkzeug.contrib.securecookie import SecureCookie

from .core import Middleware

SESSION = 0
NEVER = 'never'
NOW = 'now'
DEFAULT_EXPIRY = SESSION


class JSONCookie(SecureCookie):
    serialization_method = json

    def set_expires(self, epoch_time=NOW):
        """
        epoch_time: Unix timestamp of the cookie expiry.
        """
        if epoch_time == NOW:
            epoch_time = 123456  # a day and a half after the epoch (long ago)
        self['_expires'] = epoch_time


class SignedCookieMiddleware(Middleware):
    def __init__(self,
                 arg_name='cookie',
                 cookie_name=None,
                 secret_key=None,
                 domain=None,
                 path='/',
                 secure=False,
                 http_only=False,
                 expiry=SESSION,
                 data_expiry=None):
        if data_expiry is not None:
            print("SignedCookieMiddleware's data_expiry argument is deprecated"
                  ". Use expiry instead.")
            expiry = data_expiry
        self.arg_name = arg_name
        self.provides = (arg_name,)
        if cookie_name is None:
            cookie_name = 'clastic_%s' % arg_name
        self.cookie_name = cookie_name
        self.secret_key = secret_key or self._get_random()
        self.domain = domain  # used for cross-domain cookie
        self.path = path  # limit cookie to given path
        self.secure = secure  # only transmit on HTTPS
        self.http_only = http_only  # disallow client-side (js) access
        self.expiry = expiry

    def request(self, next, request):
        cookie = JSONCookie.load_cookie(request,
                                        key=self.cookie_name,
                                        secret_key=self.secret_key)
        response = next(**{self.arg_name: cookie})
        if self.expiry != NEVER and self.expiry != SESSION:
            # let the cookie-specified value override, if present
            if '_expires' not in cookie:
                cookie['_expires'] = time.time() + self.expiry
        save_cookie_kwargs = dict(key=self.cookie_name,
                                  domain=self.domain,
                                  path=self.path,
                                  secure=self.secure,
                                  httponly=self.http_only)
        if '_expires' in cookie:
            save_cookie_kwargs['expires'] = cookie['_expires']
        cookie.save_cookie(response, **save_cookie_kwargs)

        return response

    def _get_random(self):
        return os.urandom(20)

    def __repr__(self):
        cn = self.__class__.__name__
        return ('%s(arg_name=%r, cookie_name=%r)'
                % (cn, self.arg_name, self.cookie_name))


"""# Werkzeug cookie notes:

Very messy handling around expirations. There's an expiration for the
data ('_expires' key) that doesn't necessarily correspond to the
expiration for the cookie itself. Instead, it's serialized in,
effectively presenting a cleared cookie at deserialization time,
without actually removing the cookie from the client's browser.

Then there's also 'expires' and 'session_expires' arguments to the
save_cookie and serialize methods.

There's also the max_age argument, but since IE didn't add support for
the Max-Age cookie flag forever, usage isn't really recommended
practice, to say the least.

# Clastic integration notes:

Clastic's approach to this mess has been to try and unify the
expiration interface. Not only is data expired so it won't be
serialized back in, but the best attempt is made to line up the
expiration times so the cookie is cleared from the browser.

"""
