import datetime
import json
from flask import request
from test_base import BaseTestCase
from chessquick.models import Users, Matches, Rounds

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

    def test_submit_move_view_function_creates_adds_match_and_rounds_to_db(self):
        fen = 'rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR w KQkq'
        with self.app.test_client() as client:
            resp = client.get('/_submit_move?match_url={}&message={}&fen_move={}&current_player={}'.format('/',
                                                                                                           'message 1',
                                                                                                           fen,
                                                                                                           'w'))
            resp_data_converted_from_bytes = resp.data.decode('utf-8')
            data = json.loads(resp_data_converted_from_bytes)
            
