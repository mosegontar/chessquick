import json
import string
import random

from sqlalchemy import or_, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from chessquick import app, db, bcrypt


class Users(db.Model):
    """Users model"""

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
                              primaryjoin='or_(Users.id==Matches.white_player_id, \
                                           Users.id==Matches.black_player_id)',
                              backref=db.backref('players', lazy='dynamic', uselist=True),
                              lazy='dynamic')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        """Sets bcrypt-hashed password based on user password"""

        # encoding/decoding utf-8:
        # http://stackoverflow.com/questions/34548846/flask-bcrypt-valueerror-invalid-salt
        self._password = bcrypt.generate_password_hash(plaintext.encode('utf-8')).decode('utf-8')

    def is_correct_password(self, plaintext):
        """Confirms password by checking its hash"""

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
        """Add user to database and return instance"""
        
        user = Users(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user


    def get_recent_matches(self):
        """Return list of user's recent matches, sorted by date of last move"""

        matches = self.matches.all()
        recent_matches = sorted([(match, max(r.date_of_turn for r in match.rounds)) \
                                for match in matches], key=lambda x: x[1])

        return recent_matches

    def get_color_and_notify(self, match):
        """Return a tuple with player's color and notify status for match"""

        matches = self.matches.all()
        if match in matches:
            if match.white_player == self:
                return ('w', match.white_notify)
            else:
                return ('b', match.black_notify)
        else:
            return (False, False)

    def save_match(self, current_player, match):
        """Save match for user"""

        if current_player == 'w':
            match.white_player = self
        else:
            match.black_player = self
        db.session.add(match)
        db.session.commit()


class Matches(db.Model):
    """Matches model"""

    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_url = db.Column(db.String(8), unique=True)
    white_player_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    black_player_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    white_player = db.relationship('Users', foreign_keys=[white_player_id])
    black_player = db.relationship('Users', foreign_keys=[black_player_id])
    white_notify = db.Column(db.Boolean, default=False)
    black_notify = db.Column(db.Boolean, default=False)
    rounds = db.relationship('Rounds', backref='match', lazy='dynamic')

    @staticmethod
    def start_new_match():
        """Create a new match object with unique match_url"""

        # hat tip for this idea:
        # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
        while True:
            _match_url = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
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
        """Return match instance that corresponds to given url"""

        match = Matches.query.filter_by(match_url=url).first()
        return match

    @staticmethod
    def get_state(match, authenticated_user):
        """Return the current state of the match"""
        
        state = {'current_match': match}
        if not match:
            # inital game values
            state['current_player'] = 'w'
            state['fen'] = app.config['STARTING_FEN_STRING']          
            state['match_url'] = ''
            state['round_date'] = None            
            state['taken_players'] = {'w': "Guest", 'b': "Guest"}
            state['notify'] = False
            state['posts'] = []
            return state

        match_rounds = match.rounds.all()
        state['fen'] = str(match_rounds[-1].fen_string)        
        state['match_url'] = match.match_url
        state['round_date'] = str(match_rounds[-1].date_of_turn)
        state['taken_players'] = {'w': match.white_player.username if match.white_player else 'Guest'}
        state['taken_players'].update({'b': match.black_player.username if match.black_player else 'Guest'})
        state['notify'] = False

        # Get all posts associated with this match                            
        state['posts'] = []
        for r in match_rounds:
            if r.post:
                state['posts'].append(r.post)

        if authenticated_user:
            state['player_color'], state['notify'] = authenticated_user.get_color_and_notify(match)
        
        return state

class Posts(db.Model):
    """Posts class"""

    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('Users', foreign_keys=[author_id])
    contents = db.Column(db.String(500))
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'))

    @staticmethod
    def add_post(contents, author=None):
        """Add post to database"""

        post = Posts(contents=contents)
        if author:
            post.author = author

        db.session.add(post)
        db.session.commit()

        return post


class Rounds(db.Model):
    """Rounds model"""

    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key=True)
    turn_number = db.Column(db.Integer)
    date_of_turn = db.Column(db.DateTime)
    fen_string = db.Column(db.String(80))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    post = db.relationship('Posts', uselist=False, backref='round')

    @staticmethod
    def add_turn_to_game(match_url, fen, date_of_turn, message):
        """Add match round to database"""

        current_match = Matches.get_match_by_url(match_url)

        if not current_match:

            current_match = Matches.start_new_match()
            initial_round = Rounds(turn_number=0,
                                   date_of_turn=date_of_turn,
                                   fen_string=app.config['STARTING_FEN_STRING'])
            
            current_match.rounds.append(initial_round)

            db.session.add(current_match)
            db.session.add(initial_round)
            db.session.commit()

        num_rounds = len(current_match.rounds.all()) - 1  # because starts at turn number 0
        turn_number = num_rounds + 1

        round_entry = Rounds(turn_number=turn_number, 
                             date_of_turn=date_of_turn, 
                             fen_string=fen)

        if message: 
            round_entry.post = message

        current_match.rounds.append(round_entry)

        db.session.add(round_entry)
        db.session.add(current_match)
        db.session.commit()

        return current_match.match_url


