from flask import Flask
from flask_testing import TestCase
from chessquick import app, db

class BaseTestCase(TestCase):

    def create_app(self):
        app.config['TESTING']  = True
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI']  = "sqlite://"
        return app

    def setUp(self):
        #self.app = self.create_app().test_client()
        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

