import os
from server import app
from server.middleware import AuthMiddleware
from util.config import config
from werkzeug.datastructures import EnvironHeaders
from endpoint import (
    account, comment, history, notification, post,
    profile, session, share, system, user, query
)

# set timezone as UTC
os.environ['TZ'] = 'UTC'

# add authorization middleware
app.wsgi_app = AuthMiddleware(app=app.wsgi_app, type=EnvironHeaders)

# register flask endpoints
app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(comment, url_prefix='/comments')
app.register_blueprint(history, url_prefix='/histories')
app.register_blueprint(notification, url_prefix='/notifications')
app.register_blueprint(post, url_prefix='/posts')
app.register_blueprint(profile, url_prefix='/profile')
app.register_blueprint(session, url_prefix='/session')
app.register_blueprint(share, url_prefix='/shares')
app.register_blueprint(system, url_prefix='/system')
app.register_blueprint(user, url_prefix='/users')
app.register_blueprint(query, url_prefix='/query')

if __name__ == '__main__':
    is_debug = config.app.debug
    app.run(host='0.0.0.0', port=8080, debug=is_debug)
