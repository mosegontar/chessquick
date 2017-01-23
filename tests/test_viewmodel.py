from .test_base import BaseTestCase, FIRST_MOVE_FEN
from chessquick.models import Matches, Rounds
from chessquick.viewmodel import OptionToggler


class TestOptionToggler(BaseTestCase):

    def test_can_save_game_with_OptionToggler(self):

        user = self.add_fake_users(1)[0]
        _match_url = self.add_new_round(FIRST_MOVE_FEN)
        match = Matches.get_match_by_url(_match_url)

        ot = OptionToggler(user, 'w', match)
        ot.save_game()

        self.assertEqual(user.matches.first(), match)
