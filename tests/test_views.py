import datetime
import json
from test_base import BaseTestCase, INITIAL_FEN, FIRST_MOVE_FEN, SECOND_MOVE_FEN
from chessquick.models import Users, Matches, Rounds



class TestViews(BaseTestCase):

    def test_home_page_returns_200_status_code(self):

        response = self.client.get('/')
        self.assert200(response, "Status code != 200, got {} instead".format(response.status_code))

    def test_home_page_renders_index_template(self):

        response = self.client.get('/')
        self.assert_template_used('index.html')

    def test_home_page_renders_template_with_correct_initial_values(self):

        initial_values = {'fen': INITIAL_FEN,
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
        self.assertEqual(len(Matches.query.all()), 0)
        self.submit_move('/', FIRST_MOVE_FEN, 'w', '')
        self.assertEqual(len(Matches.query.all()), 1)
        self.assertEqual(len(Rounds.query.all()), 2)

    def test_submit_move_view_function_returns_proper_new_match_url(self):
        
        resp = self.submit_move('/', FIRST_MOVE_FEN, 'w', '')
        match = Matches.query.first()
        match_url = match.match_url
        
        resp_data_converted_from_bytes = resp.data.decode('utf-8')
        data = json.loads(resp_data_converted_from_bytes)
        
        self.assertEqual(data['match_url'], match_url)
            
