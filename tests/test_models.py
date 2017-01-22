from .test_base import BaseTestCase, INITIAL_FEN, FIRST_MOVE_FEN, SECOND_MOVE_FEN
from chessquick.models import Matches, Rounds

class TestRoundsModel(BaseTestCase):

    def test_new_round_added_to_database_successfully(self):
        self.add_new_round(FIRST_MOVE_FEN)
        round_nums = [r.turn_number for r in Rounds.query.all()]
        self.assertIn(1, round_nums)
        self.assertIn(0, round_nums)
        self.assertEqual(Rounds.query.all()[0].date_of_turn, Rounds.query.all()[1].date_of_turn)

    def test_Rounds_add_turn_to_game_creates_new_match_if_no_URL_passed(self):
        self.assertEqual(len(Matches.query.all()), 0)
        self.add_new_round(FIRST_MOVE_FEN)
        self.assertEqual(len(Matches.query.all()), 1)

    def test_newly_added_rounds_associated_with_matches_object(self):
        self.assertEqual(len(Matches.query.all()), 0)
        self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.query.first()
        self.assertEqual(len(match.rounds.all()), 2)        

class TestMatchesModel(BaseTestCase):

    def test_get_match_by_url_method_returns_None_if_passed_empty_string(self):
        match = Matches.get_match_by_url('')
        self.assertEqual(match, None)

    def test_get_match_by_url_method_returns_Match_if_passed_existing_match_url(self):
        match1_url = self.add_new_round(FIRST_MOVE_FEN)
        match2_url = self.add_new_round(FIRST_MOVE_FEN)
        self.assertNotEqual(match1_url, match2_url)
        self.assertEqual(len(Matches.query.all()), 2)
        searched_match = Matches.get_match_by_url(match2_url)
        self.assertIn(searched_match, Matches.query.all())
        self.assertEqual(searched_match.match_url, match2_url)

    def test_start_new_match_creates_correct_length_random_match_url(self):
        self.add_new_round(FIRST_MOVE_FEN)
        self.assertEqual(len(Matches.query.first().match_url), 8)

    def test_get_state_returns_initialization_values_when_passed_None(self):
        """
        frozenset used to make dict hashable for use of set operations
        """

        expected_values = {'fen': INITIAL_FEN,
                           'match_url': '',
                           'round_date': None,
                           'taken_players': frozenset({'w': "Guest", 
                                                       'b': "Guest"}.items()), 
                           'current_match': None,
                           'current_player': 'w',
                           'notify': False,
                           'posts': frozenset([])}

        state = Matches.get_state(None)
        state['taken_players'] = frozenset(state['taken_players'].items())
        state['posts'] = frozenset(state['posts'])

        unmatched = set(state.items()).symmetric_difference(set(expected_values.items()))
        self.assertEqual(len(unmatched), 0, 'Unmatched items: {}'.format(unmatched))