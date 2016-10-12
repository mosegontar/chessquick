import os
from authomatic.providers import oauth2, oauth1
import authomatic

basedir = os.path.abspath(os.path.dirname(__file__))

STARTING_FEN_STRING = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
DEBUG = True
SECRET_KEY = 'quiet'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/app'

# http://exploreflask.com/en/latest/users.html?highlight=utils
BCRYPT_LOG_ROUNDS = 12

AUTHOMATIC_SECRET = 'some secret'
AUTHOMATIC_CONFIG = {
        'twitter': {

            'class_': oauth1.Twitter,
            'consumer_key': 'coupons',
            'consumer_secret': 'buying offbrand ;}'
        },
        'google': {
            'class_': oauth2.Google,
            'consumer_key': 'https://en.wikipedia.org/wiki/Consumerism',
            'consumer_secret': 'the secret is you',
            'scope': 'it out' # https://developers.google.com/identity/protocols/googlescopes
        },
}
