from endpoint.cdn import cdn
from server import app
from server.middleware import AuthMiddleware
from util.config import config
from werkzeug.datastructures import ImmutableMultiDict

# add authorization middleware
app.wsgi_app = AuthMiddleware(app=app.wsgi_app, type=ImmutableMultiDict)

# register flask endpoints
app.register_blueprint(cdn, url_prefix='/')

if __name__ == '__main__':
    is_debug = config.app.debug
    app.run(host='0.0.0.0', port=8081, debug=is_debug)
