from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.static_folder = 'static'
app.config.from_object('config')

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
lm = LoginManager()
lm.init_app(app)

from chessquick import views, models