import json
from chessquick import app, db
from chessquick.models import Users, Matches, Rounds

class OptionToggler(object):

    def __init__(self, user, current_player, match):
        self.user = user
        self.current_player = current_player
        self.match = match
        self.color = user.get_color_and_notify(match)[0]

    def save_game(self):

        game_closed = (self.match.white_player and self.match.black_player)
        if not game_closed and (self.current_player != self.color and not self.color):
            self.user.save_match(self.current_player, self.match)

    def unsave_game(self):

        self.unnotify()

        if self.color == 'w':
            self.match.white_player = None
        if self.color == 'b':
            self.match.black_player = None

    def notify(self):
        if not self.user.email_confirmed:
            flash('For notifications, you must confirm your email.')
            return 'need confirmation'
        else:
            if self.color == 'w':
                self.match.white_notify = True
            if self.color == 'b':
                self.match.black_notify = True
       
    def unnotify(self):

        if self.color == 'w':
            self.match.white_notify = False
        if self.color == 'b':
           self.match.black_notify = False


    def commit_to_db(self):
        db.session.add(self.match)
        db.session.commit()

