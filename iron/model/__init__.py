name = 'model'

from flask_sqlalchemy import SQLAlchemy
from iron.controller import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)