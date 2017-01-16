from flask import Flask
from flask_testing import TestCase
from chessquick import app

class TestViews(TestCase):

    def create_app(self):
        self.app = app
        self.app.config['TESTING'] = True
        return self.app

    def test_home_page_returns_200_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

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
