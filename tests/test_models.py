from sqlalchemy.exc import IntegrityError
from .test_base import BaseTestCase, INITIAL_FEN, FIRST_MOVE_FEN, SECOND_MOVE_FEN
from chessquick.models import Matches, Rounds, Users
       

class TestUsersModel(BaseTestCase):

    def test_can_add_user_with_local_email_to_db(self):
        self.assertEqual(len(Users.query.all()), 0)
        user = self.add_fake_users(1)[0]
        self.assertEqual(len(Users.query.all()), 1)
        self.assertTrue(Users.query.first() == user)

    def test_user_matches_initially_zero(self):
        user = self.add_fake_users(1)[0]
        self.assertEqual(len(user.matches.all()), 0)

    def test_local_user_email_not_initally_confirmed(self):
        user = self.add_fake_users(1)[0]
        self.assertFalse(user.email_confirmed)

    def test_cannot_have_users_with_duplicate_emails(self):

        user1 = self.add_fake_users(1)[0]            
        with self.assertRaises(IntegrityError):
            user = Users.add_user(username='user{}'.format(2), 
                                  email='user{}@chessquick.com'.format(1), 
                                  password='u{}pass'.format(2), 
                                  login_type='local')

    def test_cannot_have_users_with_duplicate_usernames(self):

        user1 = self.add_fake_users(1)[0]            
        with self.assertRaises(IntegrityError):
            user = Users.add_user(username='user{}'.format(1), 
                                  email='user{}@chessquick.com'.format(2), 
                                  password='u{}pass'.format(2), 
                                  login_type='local')

    def test_local_user_password_is_hashed(self):
        user = self.add_fake_users(1)[0]
        self.assertNotEqual('u1pass', user._password)

    def test_user_can_save_match_successfully(self):
        
        user = self.add_fake_users(1)[0]
        self.assertEqual(len(user.matches.all()), 0)

        match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(match_url)

        user.save_match('w', match)
        self.assertEqual(len(user.matches.all()), 1)
        self.assertEqual(match.white_player, user)


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


    def test_match_object_knows_which_color_is_played_by_which_user(self):
        
        user1, user2 = self.add_fake_users(2)
        
        match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(match_url)
        user1.save_match('w', match)
        user2.save_match('b', match)

        self.assertNotEqual(match.white_player, user2)
        self.assertEqual(match.black_player, user2)
        self.assertEqual(match.white_player, user1)

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