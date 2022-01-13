from flask import Flask

app = Flask('spectrome', static_url_path='/s')
app.config['WTF_CSRF_ENABLED'] = False
app.config['JSON_AS_ASCII'] = False
