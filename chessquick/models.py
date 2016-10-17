import json
import string
import random

from sqlalchemy import or_, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from chessquick import app, db, bcrypt

class Users(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    auth_id = db.Column(db.String(64))
    login_type = db.Column(db.String(12))
    # http://stackoverflow.com/questions/37156248/flask-sqlalchemy-multiple-foreign-keys-in-relationship
    matches = db.relationship('Matches', 
                              primaryjoin='or_(Users.id==Matches.white_player_id, Users.id==Matches.black_player_id)',
                              backref=db.backref('players', lazy='dynamic', uselist=True),
                              lazy='dynamic')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        # encoding/decoding utf-8: 
        # http://stackoverflow.com/questions/34548846/flask-bcrypt-valueerror-invalid-salt
        self._password = bcrypt.generate_password_hash(plaintext.encode('utf-8')).decode('utf-8')


    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)


    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
    
    @staticmethod
    def add_user(**kwargs):
        user = Users(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user


    def get_recent_matches(self):

        matches = self.matches.all()
        recent_matches = sorted([(match, max(r.date_of_turn for r in match.rounds)) \
                                for match in matches], key=lambda x: x[1])

        return recent_matches

    def is_color(self, match):
        matches = self.matches.all()
        if match in matches:
            if match.white_player == self:
                return 'w'
            else:
                return 'b'
        else:
            return False

    def save_match(self, current_player, match):
        if current_player == 'w':
            match.white_player = self
        else:
            match.black_player = self
        db.session.add(match)
        db.session.commit()



class Matches(db.Model):

    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_url = db.Column(db.String(8), unique=True)
    white_player_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    black_player_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    _white_player = db.relationship('Users', foreign_keys=[white_player_id])
    _black_player = db.relationship('Users', foreign_keys=[black_player_id])
    white_notify = db.Column(db.Boolean, default=False)
    black_notify = db.Column(db.Boolean, default=False)
    rounds = db.relationship('Rounds', backref='match', lazy='dynamic')

    @staticmethod
    def start_new_match():

        while True:
            _match_url = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)\
                for _ in range(8))
            _url_exists = Matches.query.filter_by(match_url=_match_url).first()
            if not _url_exists:
                break

        new_match = Matches(match_url=_match_url)
        db.session.add(new_match)
        db.session.commit()

        return new_match

    @staticmethod
    def get_match_by_url(url):
        match = Matches.query.filter_by(match_url=url).first()
        return match

    @hybrid_property
    def white_player(self):
        return self._white_player

    @white_player.setter
    def _set_white_player(self, user):
        self._white_player = user

    @hybrid_property
    def black_player(self):
        return self._black_player

    @black_player.setter
    def _set_black_player(self, user):
        self._black_player = user

    def get_state_as_json(self):
        state = {'match_url': self.match_url,
                 'white_notify': self.white_notify,
                 'black_notify': self.black_notify}

        state['recent_move'] = str(self.rounds.all()[-1].date_of_turn)
        state['recent_fen'] = str(self.rounds.all()[-1].fen_string)
        state['players'] = {'w': self._white_player.username if self.white_player else 'Guest',
                            'b': self._black_player.username if self.black_player else 'Guest'}
        
        json_state = json.dumps(state)

        return json_state


class Rounds(db.Model):
    """Rounds model"""

    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key = True)
    turn_number = db.Column(db.Integer)
    date_of_turn = db.Column(db.DateTime)
    fen_string = db.Column(db.String(80))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

    @staticmethod
    def add_turn_to_game(match_url, fen, date_of_turn):

        current_match = Matches.query.filter_by(match_url=match_url).first()
        
        if not current_match:

            current_match = Matches.start_new_match()
            initial_round = Rounds(turn_number=0,
                                   date_of_turn=date_of_turn,
                                   fen_string=app.config['STARTING_FEN_STRING'])
            
            current_match.rounds.append(initial_round)

            db.session.add(current_match)
            db.session.add(initial_round)
            db.session.commit()

        num_rounds = len(current_match.rounds.all()) - 1 # because starting position is turn number 0
        turn_number = num_rounds + 1

        round_entry = Rounds(turn_number=turn_number, 
                             date_of_turn=date_of_turn, 
                             fen_string=fen)


        current_match.rounds.append(round_entry)

        db.session.add(round_entry)
        db.session.add(current_match)
        db.session.commit()

        return current_match.match_url
