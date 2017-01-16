import datetime

from flask import Flask, request
from flask_testing import TestCase
from chessquick import app, db
from chessquick.models import Users, Matches, Rounds

INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
FIRST_MOVE_FEN = 'rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR w KQkq'
SECOND_MOVE_FEN = 'rnbqkbnr/pppp1ppp/4p3/8/8/4P3/PPPP1PPP/RNBQKBNR w KQkq'

class BaseTestCase(TestCase):

    def create_app(self):
        app.config['TESTING']  = True
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI']  = "sqlite://"
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

    def add_new_round(self, fen_string, url=''):
        date_of_turn = datetime.datetime.utcnow()
        match_url = Rounds.add_turn_to_game(url, fen_string, date_of_turn, None)
        return match_url

    def submit_move(self, match_url, fen_move, current_player, message):
        with self.app.test_client() as client:
            response = client.get('/_submit_move?match_url={}&'\
                                  'message={}&fen_move={}&current_player={}'.\
                                  format(match_url, message, fen_move, current_player))
            return response
