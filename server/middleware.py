from .message import Message
from .session import Session
from util import Strings
from werkzeug.wrappers import Request
from werkzeug.datastructures import EnvironHeaders


class AuthMiddleware:
    def __init__(self, app, type):
        self._app = app
        self._type = type

    def __call__(self, environ, response):
        request = Request(environ)

        non_session = [
            '/session/refresh',
            '/account/create',
            '/account/activate',
            '/account/activation',
            '/account/forgot',
            '/account/reset',
            '/account/login',
            '/system/ping',
            '/system/term',
            '/system/version',
        ]
        if request.path in non_session:
            # route the response in the endpoint etc.
            return self._app(environ, response)

        if self._type == EnvironHeaders:
            auth = request.headers.get('x-authorization')
        else:
            auth = request.args.get('auth')

        mime_type = 'application/json'

        if Strings.is_empty(auth):
            content = Message('Authorization failed.')

            # return fail message if authorization missing etc.
            r = content.json()
            r.status_code = 401
            r.mimetype = mime_type
            return r(environ, response)

        # check existence of session
        exists = Session.exists(auth)
        if not exists:
            content = Message(
                message='Session expired.',
                expired=True,
            )

            # return fail message if authorization missing etc.
            r = content.json()
            r.status_code = 401
            r.mimetype = mime_type
            return r(environ, response)

        # route the response in the endpoint etc.
        return self._app(environ, response)
