import unittest
import datetime
import json
from test_base import BaseTestCase, INITIAL_FEN, FIRST_MOVE_FEN, SECOND_MOVE_FEN
from chessquick.models import Matches, Rounds


class TestViews(BaseTestCase):

    def read_json_object(self, data):

        converted_from_bytes = data.decode('utf-8')
        return json.loads(converted_from_bytes)

    def test_home_page_returns_200_status_code(self):

        response = self.client.get('/')
        self.assert200(response, 
                       "Status code != 200, got {} instead".format(response.status_code))

    def test_home_page_renders_index_template(self):
        self.client.get('/')
        self.assert_template_used('index.html')

    def test_home_page_renders_template_with_correct_initial_values(self):

        initial_values = {'fen': INITIAL_FEN,
                          'match_url': '',
                          'round_date': None,
                          'taken_players': {'w': "Guest", 'b': "Guest"},
                          'current_match': None,
                          'notify': False,
                          'posts': []}

        self.client.get('/')
        context_variables = [(key, self.get_context_variable(key)) for key in sorted(initial_values.keys())]
        self.assertEqual(context_variables, sorted(initial_values.items()))

    def test_submit_move_view_creates_adds_match_and_rounds_to_db(self):
        self.assertEqual(len(Matches.query.all()), 0)
        self.submit_move('/', FIRST_MOVE_FEN, 'w', '')
        self.assertEqual(len(Matches.query.all()), 1)
        self.assertEqual(len(Rounds.query.all()), 2)

    def test_submit_move_view_function_returns_proper_new_match_url(self):
        
        resp = self.submit_move('/', FIRST_MOVE_FEN, 'w', '')
        match = Matches.query.first()
        match_url = match.match_url
        
        data = self.read_json_object(resp.data)
        
        self.assertEqual(data['match_url'], match_url)

    def test_submit_move_view_function_returns_proper_existing_match_url(self):

        match_url = self.add_new_round(FIRST_MOVE_FEN)

        resp = self.submit_move(match_url, SECOND_MOVE_FEN, 'b', '')
        data = self.read_json_object(resp.data)
        
        self.assertEqual(match_url, data['match_url'])



            
