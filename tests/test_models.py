import datetime
import json
from test_base import BaseTestCase
from chessquick.models import Users, Matches, Rounds

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