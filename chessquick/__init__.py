from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from authomatic import Authomatic

app = Flask(__name__, instance_relative_config=True)
app.static_folder = 'static'
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

authomatic = Authomatic(app.config['AUTHOMATIC_CONFIG'], app.config['AUTHOMATIC_SECRET'])


from chessquick import views, models