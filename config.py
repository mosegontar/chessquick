import os
from authomatic.providers import oauth2, oauth1
import authomatic

basedir = os.path.abspath(os.path.dirname(__file__))

STARTING_FEN_STRING = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', default="sqlite:///")

# http://exploreflask.com/en/latest/users.html?highlight=utils
BCRYPT_LOG_ROUNDS = 12

AUTHOMATIC_SECRET = 'some secret'
AUTHOMATIC_CONFIG = {
        'google': {
            'class_': oauth2.Google,
            'consumer_key': os.environ.get('GOOGLE_CONSUMER_KEY'),
            'consumer_secret': os.environ.get('GOOGLE_CONSUMER_SECRET'),
            'scope': ['profile', 'email']
        },
}

# mail server settings
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# Admins
ADMINS = [os.environ.get('ADMIN_EMAIL')]

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_DEFAULT_FROM = 'chessquick@chessquick.com'