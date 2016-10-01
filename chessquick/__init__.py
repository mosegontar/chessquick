from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.static_folder = 'static'
app.config.from_object('config')

db = SQLAlchemy(app)
from chessquick import views, models