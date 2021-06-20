from flask import Flask
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix
name = 'ctrl'

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Iron API',
          description='The Iron API')
