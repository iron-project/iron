from flask_sqlalchemy import SQLAlchemy
from iron.ctrl import app

name = 'model'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
