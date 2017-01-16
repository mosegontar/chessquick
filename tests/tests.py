import datetime
from flask import Flask
from flask_testing import TestCase
from chessquick import app, db
from chessquick.models import Users, Matches, Rounds

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

class TestViews(BaseTestCase):

    def test_home_page_returns_200_status_code(self):

        response = self.client.get('/')
        self.assert200(response, "Status code != 200, got {} instead".format(response.status_code))

    def test_home_page_renders_index_template(self):

        response = self.client.get('/')
        self.assert_template_used('index.html')

    def test_home_page_renders_template_with_correct_initial_values(self):

        initial_values = {'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                          'match_url': '',
                          'round_date': None,
                          'taken_players': {'w': "Guest", 'b': "Guest"},
                          'current_match': None,
                          'notify': False,
                          'posts': []}

        response = self.client.get('/')
        context_variables = [(key, self.get_context_variable(key)) for key, value in sorted(initial_values.items())]
        self.assertEqual(context_variables, sorted(initial_values.items()))

class TestModels(BaseTestCase):

    def add_new_round(self):
        url = ''
        fen = 'rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR w KQkq'
        date_of_turn = datetime.datetime.utcnow()
        Rounds.add_turn_to_game(url, fen, date_of_turn, None)
        return url, fen, date_of_turn

    def test_new_round_added_to_database_successfully(self):
        url, fen, date_of_turn = self.add_new_round()
        round_nums = [r.turn_number for r in Rounds.query.all()]
        self.assertIn(1, round_nums)
        self.assertIn(0, round_nums)
        self.assertEqual(Rounds.query.all()[0].date_of_turn, Rounds.query.all()[1].date_of_turn)

    def test_get_match_by_url_returns_None_if_passed_empty_string(self):
        match = Matches.get_match_by_url('')
        self.assertEqual(match, None)

    def test_Rounds_add_turn_to_game_creates_new_match_if_no_URL_passed(self):
        self.assertEqual(len(Matches.query.all()), 0)
        self.add_new_round()
        self.assertEqual(len(Matches.query.all()), 1)

    def test_Matches_start_new_match_creates_correct_length_random_match_url(self):
        self.add_new_round()
        self.assertEqual(len(Matches.query.first().match_url), 8)

    def test_newly_added_rounds_associated_with_matches_object(self):
        self.assertEqual(len(Matches.query.all()), 0)
        self.add_new_round()
        self.assertEqual(len(Matches.query.all()), 1)
        
        match = Matches.query.first()
        self.assertEqual(len(match.rounds.all()), 2)