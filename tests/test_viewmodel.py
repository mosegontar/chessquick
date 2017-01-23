from .test_base import BaseTestCase, FIRST_MOVE_FEN
from chessquick.models import Matches, Rounds
from chessquick.viewmodel import OptionToggler


class TestOptionToggler(BaseTestCase):

    def test_can_save_open_game(self):

        user = self.add_fake_users(1)[0]
        _match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(_match_url)

        ot = OptionToggler(user, 'w', match)
        ot.save_game()

        self.assertEqual(user.matches.first(), match)
        self.assertEqual(match.white_player, user)

    def test_cannot_save_closed_game(self):

        user1, user2, user3 = self.add_fake_users(3)
        _match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(_match_url)

        user1.save_match('w', match)      
        user3.save_match('b', match)

        ot = OptionToggler(user2, 'w', match)
        ot.save_game()

        self.assertIsNone(user2.matches.first())

    def test_can_unsave_game(self):

        user1, user2 = self.add_fake_users(2)
        _match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(_match_url)

        user1.save_match('w', match)      
        user2.save_match('b', match)

        self.assertEqual(user1.matches.first(), match)
        self.assertEqual(user2.matches.first(), match)        
        self.assertEqual(match.white_player, user1)        
        self.assertEqual(match.black_player, user2)

        ot = OptionToggler(user2, 'w', match)
        ot.unsave_game()

        self.assertEqual(user1.matches.first(), match)
        self.assertNotEqual(user2.matches.first(), match)        
        self.assertEqual(match.white_player, user1)        
        self.assertNotEqual(match.black_player, user2)        

    def test_cannot_set_notify_True_if_email_unconfirmed(self):

        user = self.add_fake_users(1)[0]
        _match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(_match_url)

        ot = OptionToggler(user, 'w', match)
        ot.save_game()

        self.assertEqual('need confirmation', ot.notify())

    def test_can_set_notify_True_if_email_unconfirmed(self):

        user = self.add_fake_users(1)[0]
        user.email_confirmed = True
        _match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(_match_url)
        user.save_match('w', match)
        
        ot = OptionToggler(user, 'w', match)
        self.assertEqual(match.white_notify, False)        
        ot.notify()
        
        self.assertEqual(match.white_notify, True)        





